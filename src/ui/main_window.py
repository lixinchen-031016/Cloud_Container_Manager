"""
主窗口模块
应用的主要界面框架
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QMenuBar, QMenu,
    QLabel, QFrame, QListWidget, QListWidgetItem,
    QMessageBox, QSplitter, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssh_client import SSHClient, SSHConfig
from core.config_manager import ConfigManager
from ui.connection_dialog import ConnectionDialog
from ui.server_monitor import ServerMonitorPanel
from ui.container_manager import ContainerManagerPanel


class ServerConnectionItem:
    """服务器连接项数据"""
    
    def __init__(self, config: SSHConfig):
        self.config = config
        self.client = SSHClient()
        self.connected = False
    
    def connect(self) -> tuple:
        """建立连接"""
        success, message = self.client.connect(self.config)
        if success:
            self.connected = True
        return success, message
    
    def disconnect(self):
        """断开连接"""
        self.client.disconnect()
        self.connected = False


class MainWindow(QMainWindow):
    """应用主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_connection: Optional[ServerConnectionItem] = None
        self.config_manager = ConfigManager()
        
        self._init_ui()
        self._create_menu_bar()
        self._load_saved_servers()
        self._apply_styles()
    
    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Cloud Container Manager")
        self.setMinimumSize(1200, 800)
        
        # 中心 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧边栏（服务器列表）
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFixedWidth(1)
        main_layout.addWidget(separator)
        
        # 右侧内容区域
        content_area = self._create_content_area()
        main_layout.addWidget(content_area, 1)  # 拉伸因子为 1
        
        central_widget.setLayout(main_layout)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪 - 请连接服务器")
    
    def _create_sidebar(self) -> QWidget:
        """创建侧边栏"""
        widget = QWidget()
        widget.setMaximumWidth(250)
        widget.setMinimumWidth(200)
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题区域
        title_frame = QFrame()
        title_frame.setObjectName("sidebarTitle")
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel("服务器")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        title_layout.addWidget(title_label)
        
        add_btn = QPushButton("+ 添加服务器")
        add_btn.setObjectName("addServerBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_server)
        title_layout.addWidget(add_btn)
        
        title_frame.setLayout(title_layout)
        layout.addWidget(title_frame)
        
        # 服务器列表
        self.server_list = QListWidget()
        self.server_list.setObjectName("serverList")
        self.server_list.itemClicked.connect(self._on_server_selected)
        self.server_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.server_list.customContextMenuRequested.connect(self._show_server_context_menu)
        layout.addWidget(self.server_list)
        
        widget.setLayout(layout)
        return widget
    
    def _create_content_area(self) -> QWidget:
        """创建内容区域"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setEnabled(False)  # 初始禁用，直到连接成功
        
        # 服务器监控标签页
        self.monitor_panel = ServerMonitorPanel(SSHClient())
        self.tabs.addTab(self.monitor_panel, "📊 服务器监控")
        
        # 容器管理标签页
        self.container_panel = ContainerManagerPanel(SSHClient())
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
        
        # 打开终端
        terminal_action = QAction("打开终端 (&T)", self)
        terminal_action.setShortcut("Ctrl+Shift+T")
        terminal_action.triggered.connect(self._open_terminal)
        file_menu.addAction(terminal_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出 (&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具 (&T)")
        
        # 打开本地终端
        local_terminal_action = QAction("本地终端 (&L)", self)
        local_terminal_action.triggered.connect(self._open_local_terminal)
        tools_menu.addAction(local_terminal_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助 (&H)")
        
        about_action = QAction("关于 (&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            #sidebarTitle {
                background-color: #e0e0e0;
                border-bottom: 1px solid #ccc;
            }
            
            #addServerBtn {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                margin: 5px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            #addServerBtn:hover {
                background-color: #45a049;
            }
            
            #serverList {
                border: none;
                background-color: white;
                outline: none;
            }
            
            #serverList::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            
            #serverList::item:selected {
                background-color: #e3f2fd;
                color: #1976D2;
            }
            
            #serverList::item:hover {
                background-color: #f5f5f5;
            }
            
            #mainTabs {
                background-color: white;
                border: none;
            }
            
            #mainTabs::pane {
                border: none;
                background-color: white;
            }
            
            #mainTabs::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 10px 20px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
            
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #eee;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
            }
            
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
            }
            
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #ccc;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #aaa;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def _add_server(self):
        """添加服务器"""
        dialog = ConnectionDialog(self)
        dialog.connected.connect(self._on_server_connected)
        dialog.exec()
    
    def _on_server_connected(self, config: SSHConfig, save_password: bool = False):
        """服务器连接成功回调"""
        # 创建连接项
        connection = ServerConnectionItem(config)
        success, message = connection.connect()
        
        if not success:
            QMessageBox.critical(self, "连接失败", message)
            return
        
        # 添加到列表
        server_name = f"{config.username}@{config.hostname}"
        item = QListWidgetItem(server_name)
        item.setData(Qt.ItemDataRole.UserRole, connection)
        self.server_list.addItem(item)
        
        # 保存配置（根据用户选择决定是否保存密码）
        self.config_manager.add_server(config, save_password=save_password)
        
        # 选中该项
        self.server_list.setCurrentItem(item)
        
        self.statusBar.showMessage(f"已连接到 {config.hostname}")
    
    def _load_saved_servers(self):
        """加载保存的服务器配置"""
        servers = self.config_manager.get_servers()
        for i, server_data in enumerate(servers):
            # 创建显示项，但不自动连接
            server_name = server_data.get('name', f"{server_data['username']}@{server_data['hostname']}")
            item = QListWidgetItem(server_name)
            # 存储配置数据，用户点击时再连接
            item.setData(Qt.ItemDataRole.UserRole, {
                'type': 'saved_config',
                'config_index': i,  # 保存索引以便获取解密的密码
                'config_data': server_data
            })
            self.server_list.addItem(item)
    
    def _show_server_context_menu(self, pos):
        """显示服务器右键菜单"""
        # 获取点击位置的项
        item = self.server_list.itemAt(pos)
        if not item:
            return
        
        # 获取项的索引
        row = self.server_list.row(item)
        data = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        # 删除选项
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_server(row))
        menu.addAction(delete_action)
        
        menu.exec(self.server_list.viewport().mapToGlobal(pos))
    
    def _delete_server(self, index: int):
        """删除服务器配置"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除此服务器配置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 从配置管理器删除
        self.config_manager.remove_server(index)
        # 从列表删除
        self.server_list.takeItem(index)
    
    def _on_server_selected(self, item: QListWidgetItem):
        """服务器列表项被选中"""
        data = item.data(Qt.ItemDataRole.UserRole)
        
        if not data:
            return
        
        # 如果是已保存的配置（需要重新连接）
        if isinstance(data, dict) and data.get('type') == 'saved_config':
            config_data = data['config_data']
            # 显示连接对话框，预填充信息
            self._connect_to_saved_server(config_data, item)
            return
        
        # 如果是已连接的服务器
        connection = data
        if not isinstance(connection, ServerConnectionItem):
            return
        
        # 如果未连接，尝试连接
        if not connection.connected:
            print(f"[DEBUG] 正在连接到 {connection.config.hostname}...")
            success, message = connection.connect()
            if not success:
                print(f"[ERROR] 连接失败：{message}")
                QMessageBox.critical(self, "连接失败", message)
                return
            print(f"[DEBUG] 连接成功！SSH 客户端对象 ID: {id(connection.client)}")
        
        # 切换到当前连接
        self.current_connection = connection
        
        # 更新面板的 SSH 客户端
        print(f"[DEBUG] 更新监控面板的 SSH 客户端到：{id(connection.client)}")
        self.monitor_panel.ssh_client = connection.client
        self.container_panel.ssh_client = connection.client
        self.container_panel.docker_client = DockerClient(connection.client)
        
        # 启用标签页
        self.tabs.setEnabled(True)
        
        # 停止之前的监控（如果有）
        self.monitor_panel.stop_monitoring()
        self.container_panel.stop_monitoring()
        
        # 启动监控
        print(f"[DEBUG] 开始监控...")
        self.monitor_panel.start_monitoring()
        self.container_panel.start_monitoring()
        
        self.statusBar.showMessage(f"当前服务器：{connection.config.hostname}")
    
    def _connect_to_saved_server(self, config_data: dict, item: QListWidgetItem):
        """连接到保存的服务器"""
        from ui.connection_dialog import ConnectionDialog
        
        # 尝试使用保存的密码直接连接
        config_index = config_data.get('config_index', 0)
        saved_config = self.config_manager.get_server_config(config_index)
        
        if saved_config and (saved_config.password or saved_config.key_filename):
            # 有保存的认证信息，直接尝试连接
            print(f"[DEBUG] 使用保存的认证信息连接 {saved_config.hostname}")
            connection = ServerConnectionItem(saved_config)
            success, message = connection.connect()
            
            if success:
                # 连接成功，直接使用
                server_name = f"{saved_config.username}@{saved_config.hostname}"
                item.setText(server_name)
                item.setData(Qt.ItemDataRole.UserRole, connection)
                self._on_server_selected(item)
                return
            else:
                print(f"[DEBUG] 自动连接失败：{message}，要求用户重新输入")
        
        # 没有保存的认证信息或自动连接失败，显示对话框
        dialog = ConnectionDialog(self)
        # 预填充主机和用户名
        dialog.host_input.setText(config_data['hostname'])
        dialog.port_input.setValue(config_data['port'])
        dialog.username_input.setText(config_data['username'])
        
        dialog.connected.connect(lambda config, save=False: self._on_saved_server_connected(config, item, save))
        dialog.exec()
    
    def _on_saved_server_connected(self, config: SSHConfig, item: QListWidgetItem, save_password: bool = False):
        """保存的服务器连接成功回调"""
        # 创建连接项
        connection = ServerConnectionItem(config)
        success, message = connection.connect()
        
        if not success:
            QMessageBox.critical(self, "连接失败", message)
            return
        
        # 更新列表项数据
        server_name = f"{config.username}@{config.hostname}"
        item.setText(server_name)
        item.setData(Qt.ItemDataRole.UserRole, connection)
        
        # 如果选择保存密码，更新配置
        if save_password:
            config_index = item.data(Qt.ItemDataRole.UserRole).get('config_index') if isinstance(item.data(Qt.ItemDataRole.UserRole), dict) else None
            if config_index is not None:
                self.config_manager.update_server(config_index, config, save_password=True)
        
        # 自动选中并连接
        self._on_server_selected(item)
        
        self.statusBar.showMessage(f"已连接到 {config.hostname}")
    
    def _open_terminal(self):
        """打开系统终端连接到当前服务器"""
        if not self.current_connection or not self.current_connection.connected:
            QMessageBox.warning(
                self,
                "未连接",
                "请先连接到一个服务器"
            )
            return
        
        from core.system_terminal import SystemTerminal
        
        try:
            SystemTerminal.open_terminal(self.current_connection.config)
            self.statusBar.showMessage(f"已打开终端窗口连接到 {self.current_connection.config.hostname}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "打开终端失败",
                f"无法打开系统终端：{str(e)}\n\n请确保 macOS 的 Terminal.app 可用。"
            )
    
    def _open_local_terminal(self):
        """打开本地终端"""
        from core.system_terminal import SystemTerminal
        
        try:
            SystemTerminal.open_local_terminal()
            self.statusBar.showMessage("已打开本地终端窗口")
        except Exception as e:
            QMessageBox.critical(
                self,
                "打开终端失败",
                f"无法打开本地终端：{str(e)}"
            )
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 Cloud Container Manager",
            """<h2>Cloud Container Manager</h2>
            <p>版本：1.0.4</p>
            <p>一个用于管理云端服务器和 Docker 容器的 macOS 原生应用。</p>
            <p><b>功能特性：</b></p>
            <ul>
                <li>SSH 远程连接（支持密码加密存储）</li>
                <li>服务器资源监控</li>
                <li>Docker 容器管理</li>
                <li>实时日志查看</li>
                <li>系统终端集成</li>
                <li>Docker Compose 部署</li>
            </ul>
            <p><b>技术栈：</b></p>
            <ul>
                <li>PyQt6 - GUI 框架</li>
                <li>paramiko - SSH 连接</li>
                <li>docker-py - Docker 管理</li>
                <li>cryptography - 密码加密</li>
            </ul>
            """
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有监控
        self.monitor_panel.stop_monitoring()
        self.container_panel.stop_monitoring()
        
        # 断开所有连接
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            connection = item.data(Qt.ItemDataRole.UserRole)
            if connection:
                connection.disconnect()
        
        event.accept()


# 需要导入这些类以避免循环导入问题
from ui.container_manager import ContainerManagerPanel
from core.docker_client import DockerClient
