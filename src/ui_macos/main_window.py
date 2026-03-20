"""
macOS 风格主窗口模块
Cloud Container Manager 新 UI 的主界面
"""
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QMessageBox, QMenu, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from services.service_container import ServiceContainer, SSH_SERVICE, DOCKER_SERVICE, CONFIG_SERVICE
from services.theme_service import get_theme_service

from ui_macos.widgets.themed_widget import ThemedWidget
from ui_macos.widgets.macos_sidebar import MacOsSidebar
from ui_macos.widgets.macos_button import MacOsButton
from ui_macos.dialogs.connection_dialog import ConnectionDialog
from ui_macos.panels.server_monitor import ServerMonitorPanel
from ui_macos.panels.container_manager import ContainerManagerPanel
from core.ssh_client import SSHConfig
from core.docker_client import DockerClient


class ServerConnectionItem:
    """服务器连接项数据"""
    
    def __init__(self, config: SSHConfig):
        self.config = config
        self.connected = False
    
    def connect(self, ssh_service) -> tuple:
        """建立连接"""
        success, message = ssh_service.connect(self.config)
        if success:
            self.connected = True
        return success, message
    
    def disconnect(self, ssh_service) -> None:
        """断开连接"""
        ssh_service.disconnect()
        self.connected = False


class MainWindow(QMainWindow):
    """macOS 风格主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Cloud Container Manager")
        self.setMinimumSize(1200, 800)
        
        # 获取服务实例
        container = ServiceContainer.get_instance()
        container.initialize()
        self.ssh_service = container.resolve(SSH_SERVICE)
        self.config_service = container.resolve(CONFIG_SERVICE)
        
        # 主题服务
        self.theme_service = get_theme_service()
        self.theme_service.register_widget(self)
        
        # 当前连接
        self.current_connection: Optional[ServerConnectionItem] = None
        
        # 初始化菜单栏服务
        self._init_menu_bar_service()
        
        self._init_ui()
        self._create_menu_bar()
        self._load_saved_servers()
    
    def _init_ui(self):
        """初始化 UI"""
        central_widget = ThemedWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局（包含状态栏）
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 内容区域布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧边栏
        sidebar = self._create_sidebar()
        content_layout.addWidget(sidebar)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFixedWidth(1)
        separator.setStyleSheet(f"background-color: {self.get_color('BORDER')};")
        content_layout.addWidget(separator)
        
        # 右侧内容区域（占位）
        content_area = self._create_content_area()
        content_layout.addWidget(content_area, 1)
        
        main_layout.addLayout(content_layout)
        
        # 状态栏
        self.statusBar = QLabel("就绪 - 请连接服务器")
        self.statusBar.setStyleSheet(f"""
            background-color: {self.get_card_background_color()};
            color: {self.get_secondary_text_color()};
            padding: 8px 20px;
            border-top: 1px solid {self.get_color('BORDER')};
            font-size: 12px;
        """)
        main_layout.addWidget(self.statusBar)
        
        central_widget.setLayout(main_layout)
    
    def _create_sidebar(self) -> QWidget:
        """创建侧边栏"""
        self.sidebar = MacOsSidebar(
            title="☁️ 服务器",
            show_add_button=True,
            show_search=True
        )
        
        # 连接信号
        self.sidebar.item_selected.connect(self._on_server_selected)
        self.sidebar.add_button_clicked.connect(self._add_server)
        
        return self.sidebar
    
    def _create_content_area(self) -> QWidget:
        """创建内容区域"""
        widget = ThemedWidget()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setEnabled(False)  # 初始禁用，直到连接成功
        
        # 服务器监控标签页
        self.ssh_service_for_monitor = self.ssh_service
        container = ServiceContainer.get_instance()
        self.docker_service = container.resolve(DOCKER_SERVICE)
        
        self.monitor_panel = ServerMonitorPanel(self.ssh_service_for_monitor)
        self.tabs.addTab(self.monitor_panel, "📊 服务器监控")
        
        # 容器管理标签页
        self.container_panel = ContainerManagerPanel(self.docker_service)
        self.tabs.addTab(self.container_panel, "🐳 容器管理")
        
        layout.addWidget(self.tabs)
        widget.setLayout(layout)
        return widget
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件 (&F)")
        
        # 添加服务器
        add_server_action = QAction("添加服务器 (&A)", self)
        add_server_action.setShortcut("Ctrl+N")
        add_server_action.triggered.connect(self._add_server)
        file_menu.addAction(add_server_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出 (&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助 (&H)")
        
        about_action = QAction("关于 (&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _add_server(self):
        """添加服务器"""
        dialog = ConnectionDialog(self)
        dialog.connected.connect(self._on_server_connected)
        dialog.exec()
    
    def _on_server_connected(self, config: SSHConfig, save_password: bool):
        """服务器连接成功回调"""
        # 创建连接项
        connection = ServerConnectionItem(config)
        success, message = connection.connect(self.ssh_service)
        
        if not success:
            QMessageBox.critical(self, "连接失败", message)
            return
        
        # 添加到列表
        server_name = f"{config.username}@{config.hostname}"
        item = self.sidebar.add_item(server_name, data=connection)
        
        # 保存配置
        self.config_service.add_server(config, save_password=save_password)
        
        # 选中该项
        self.sidebar.list_widget.setCurrentItem(item)
        
        self._update_status(f"已连接到 {config.hostname}")
    
    def _load_saved_servers(self):
        """加载保存的服务器配置"""
        servers = self.config_service.get_servers()
        for i, server_data in enumerate(servers):
            server_name = server_data.get('name', f"{server_data['username']}@{server_data['hostname']}")
            item = self.sidebar.add_item(server_name, data={
                'type': 'saved_config',
                'config_index': i,
                'config_data': server_data
            })
    
    def _on_server_selected(self, data: Any):
        """服务器列表项被选中"""
        if not data:
            return
        
        # 如果是已保存的配置（需要重新连接）
        if isinstance(data, dict) and data.get('type') == 'saved_config':
            self._connect_to_saved_server(data)
            return
        
        # 如果是已连接的服务器
        connection = data
        if not isinstance(connection, ServerConnectionItem):
            return
        
        # 如果未连接，尝试连接
        if not connection.connected:
            success, message = connection.connect(self.ssh_service)
            if not success:
                QMessageBox.critical(self, "连接失败", message)
                return
        
        # 切换到当前连接
        self.current_connection = connection
        self._update_status(f"当前服务器：{connection.config.hostname}")
        
        # 启用标签页
        self.tabs.setEnabled(True)
        
        # 更新监控面板的 SSH 服务
        self.monitor_panel.ssh_service = self.ssh_service
        
        # 更新容器管理面板的 Docker 服务
        docker_client = DockerClient(self.ssh_service.get_client())
        self.docker_service.set_ssh_client(self.ssh_service.get_client())
        
        # 停止之前的监控
        self.monitor_panel.stop_monitoring()
        self.container_panel.stop_monitoring()
        
        # 启动监控
        self.monitor_panel.start_monitoring()
        self.container_panel.start_monitoring()
    
    def _connect_to_saved_server(self, config_data: dict):
        """连接到保存的服务器"""
        config_index = config_data.get('config_index', 0)
        saved_config = self.config_service.get_server_config(config_index)
        
        if saved_config and (saved_config.password or saved_config.key_filename):
            # 有保存的认证信息，直接尝试连接
            connection = ServerConnectionItem(saved_config)
            success, message = connection.connect(self.ssh_service)
            
            if success:
                # 连接成功，直接使用
                server_name = f"{saved_config.username}@{saved_config.hostname}"
                # 更新列表项
                current_item, _ = self.sidebar.get_selected_item()
                if current_item:
                    current_item.setText(server_name)
                    current_item.setData(Qt.ItemDataRole.UserRole, connection)
                
                self.current_connection = connection
                self._update_status(f"已连接到 {saved_config.hostname}")
                return
        
        # 没有保存的认证信息或自动连接失败，显示对话框
        dialog = ConnectionDialog(self)
        # 预填充主机和用户名
        dialog.host_input.setText(config_data['config_data']['hostname'])
        dialog.port_input.setValue(config_data['config_data']['port'])
        dialog.username_input.setText(config_data['config_data']['username'])
        
        dialog.connected.connect(lambda config, save=False: self._on_saved_server_connected(config, save))
        dialog.exec()
    
    def _on_saved_server_connected(self, config: SSHConfig, save_password: bool):
        """保存的服务器连接成功回调"""
        # 创建连接项
        connection = ServerConnectionItem(config)
        success, message = connection.connect(self.ssh_service)
        
        if not success:
            QMessageBox.critical(self, "连接失败", message)
            return
        
        # 更新列表项数据
        server_name = f"{config.username}@{config.hostname}"
        current_item, _ = self.sidebar.get_selected_item()
        if current_item:
            current_item.setText(server_name)
            current_item.setData(Qt.ItemDataRole.UserRole, connection)
        
        # 如果选择保存密码，更新配置
        if save_password:
            # TODO: 更新配置
            pass
        
        # 自动选中并连接
        self._on_server_selected(connection)
        self._update_status(f"已连接到 {config.hostname}")
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.statusBar.setText(message)
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 Cloud Container Manager",
            """<h2>Cloud Container Manager</h2>
            <p>版本：2.0.0 (macOS UI)</p>
            <p>一个用于管理云端服务器和 Docker 容器的 macOS 原生风格应用。</p>
            <p><b>技术栈：</b></p>
            <ul>
                <li>PyQt6 - GUI 框架</li>
                <li>paramiko - SSH 连接</li>
                <li>docker-py - Docker 管理</li>
                <li>cryptography - 密码加密</li>
            </ul>
            """
        )
    
    def _init_menu_bar_service(self):
        """初始化菜单栏服务"""
        from services.menu_bar_service import get_menu_bar_service
        
        self.menu_bar_service = get_menu_bar_service()
        self.menu_bar_service.initialize()
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """主题变化处理"""
        # 更新状态栏样式（如果已创建）
        if hasattr(self, 'statusBar'):
            self.statusBar.setStyleSheet(f"""
                background-color: {self.theme_service.get_card_background_color()};
                color: {self.theme_service.get_secondary_text_color()};
                padding: 8px 20px;
                border-top: 1px solid {self.theme_service.get_color('BORDER')};
                font-size: 12px;
            """)
    
    def get_color(self, color_name: str) -> str:
        """获取当前主题颜色"""
        return self.theme_service.get_color(color_name)
    
    def get_accent_color(self) -> str:
        """获取强调色"""
        return self.theme_service.get_accent_color()
    
    def get_background_color(self) -> str:
        """获取背景色"""
        return self.theme_service.get_background_color()
    
    def get_card_background_color(self) -> str:
        """获取卡片背景色"""
        return self.theme_service.get_card_background_color()
    
    def get_text_color(self) -> str:
        """获取主要文本颜色"""
        return self.theme_service.get_text_color()
    
    def get_secondary_text_color(self) -> str:
        """获取次要文本颜色"""
        return self.theme_service.get_secondary_text_color()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止监控
        if hasattr(self, 'monitor_panel'):
            self.monitor_panel.stop_monitoring()
        
        # 断开所有连接
        if self.current_connection and self.current_connection.connected:
            self.current_connection.disconnect(self.ssh_service)
        
        # 清理菜单栏服务
        if hasattr(self, 'menu_bar_service'):
            self.menu_bar_service.cleanup()
        
        # 注销主题服务
        try:
            self.theme_service.unregister_widget(self)
        except Exception:
            pass
        
        event.accept()
