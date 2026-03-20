"""
macOS 风格连接对话框模块
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTabWidget, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional

from core.ssh_client import SSHConfig
from ui_macos.widgets.themed_widget import ThemedWidget
from ui_macos.widgets.macos_button import MacOsButton


class ConnectionDialog(QDialog):
    """macOS 风格 SSH 连接配置对话框"""
    
    # 连接成功信号
    connected = pyqtSignal(SSHConfig, bool)  # config, save_password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接到服务器")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # 获取主题服务
        from services.theme_service import get_theme_service
        self._theme_service = get_theme_service()
        self._is_dark_mode = self._theme_service.is_dark_mode()
        
        self._init_ui()
    
    def get_color(self, color_name: str) -> str:
        """获取当前主题颜色"""
        return self._theme_service.get_color(color_name)
    
    def get_accent_color(self) -> str:
        """获取强调色"""
        return self._theme_service.get_accent_color()
    
    def get_background_color(self) -> str:
        """获取背景色"""
        return self._theme_service.get_background_color()
    
    def get_card_background_color(self) -> str:
        """获取卡片背景色"""
        return self._theme_service.get_card_background_color()
    
    def get_text_color(self) -> str:
        """获取主要文本颜色"""
        return self._theme_service.get_text_color()
    
    def get_secondary_text_color(self) -> str:
        """获取次要文本颜色"""
        return self._theme_service.get_secondary_text_color()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("🔐 连接到服务器")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.get_text_color()};
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # 创建标签页（密码认证 / 密钥认证）
        tabs = QTabWidget()
        tabs.setObjectName("authTabs")
        
        # 密码认证页面
        password_widget = self._create_password_auth_page()
        tabs.addTab(password_widget, "密码认证")
        
        # 密钥认证页面
        key_widget = self._create_key_auth_page()
        tabs.addTab(key_widget, "密钥认证")
        
        self.tabs = tabs
        layout.addWidget(tabs)
        
        # 记住密码选项
        self.remember_password_checkbox = QCheckBox("记住密码（加密存储）")
        self.remember_password_checkbox.setChecked(False)
        self.remember_password_checkbox.setStyleSheet(f"""
            color: {self.get_secondary_text_color()};
            font-size: 13px;
        """)
        layout.addWidget(self.remember_password_checkbox)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(self._get_secondary_button_style())
        btn_layout.addWidget(cancel_btn)
        
        connect_btn = MacOsButton("连接", is_primary=True)
        connect_btn.clicked.connect(self._connect)
        btn_layout.addWidget(connect_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # 应用主题
        self._apply_theme_to_tabs()
    
    def _create_password_auth_page(self) -> QWidget:
        """创建密码认证页面"""
        widget = ThemedWidget()
        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # 主机
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("例如：192.168.1.100 或 example.com")
        self.host_input.setFixedHeight(36)
        layout.addRow("主机:", self.host_input)
        
        # 端口
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        self.port_input.setFixedHeight(36)
        layout.addRow("端口:", self.port_input)
        
        # 用户名
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("例如：root")
        self.username_input.setFixedHeight(36)
        layout.addRow("用户名:", self.username_input)
        
        # 密码
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(36)
        layout.addRow("密码:", self.password_input)
        
        widget.setLayout(layout)
        return widget
    
    def _create_key_auth_page(self) -> QWidget:
        """创建密钥认证页面"""
        widget = ThemedWidget()
        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # 主机
        self.key_host_input = QLineEdit()
        self.key_host_input.setPlaceholderText("例如：192.168.1.100 或 example.com")
        self.key_host_input.setFixedHeight(36)
        layout.addRow("主机:", self.key_host_input)
        
        # 端口
        self.key_port_input = QSpinBox()
        self.key_port_input.setRange(1, 65535)
        self.key_port_input.setValue(22)
        self.key_port_input.setFixedHeight(36)
        layout.addRow("端口:", self.key_port_input)
        
        # 用户名
        self.key_username_input = QLineEdit()
        self.key_username_input.setPlaceholderText("例如：root")
        self.key_username_input.setFixedHeight(36)
        layout.addRow("用户名:", self.key_username_input)
        
        # 密钥文件
        key_file_layout = QHBoxLayout()
        self.key_file_input = QLineEdit()
        self.key_file_input.setPlaceholderText("~/.ssh/id_rsa")
        self.key_file_input.setFixedHeight(36)
        key_file_layout.addWidget(self.key_file_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedHeight(36)
        browse_btn.clicked.connect(self._browse_key_file)
        browse_btn.setStyleSheet(self._get_secondary_button_style())
        key_file_layout.addWidget(browse_btn)
        
        layout.addRow("密钥文件:", key_file_layout)
        
        # 密钥密码（可选）
        self.key_passphrase_input = QLineEdit()
        self.key_passphrase_input.setPlaceholderText("如果密钥有密码则填写")
        self.key_passphrase_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_passphrase_input.setFixedHeight(36)
        layout.addRow("密钥密码:", self.key_passphrase_input)
        
        widget.setLayout(layout)
        return widget
    
    def _browse_key_file(self):
        """浏览选择密钥文件"""
        home_dir = os.path.expanduser("~")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 SSH 密钥文件",
            os.path.join(home_dir, ".ssh"),
            "All Files (*)"
        )
        
        if file_path:
            self.key_file_input.setText(file_path)
    
    def _get_password_config(self) -> Optional[SSHConfig]:
        """获取密码认证配置"""
        host = self.host_input.text().strip()
        port = self.port_input.value()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not host or not username or not password:
            return None
        
        return SSHConfig(
            hostname=host,
            port=port,
            username=username,
            password=password
        )
    
    def _get_key_config(self) -> Optional[SSHConfig]:
        """获取密钥认证配置"""
        host = self.key_host_input.text().strip()
        port = self.key_port_input.value()
        username = self.key_username_input.text().strip()
        key_file = self.key_file_input.text().strip()
        passphrase = self.key_passphrase_input.text() or None
        
        if not host or not username or not key_file:
            return None
        
        # 展开路径
        key_file = os.path.expanduser(key_file)
        
        return SSHConfig(
            hostname=host,
            port=port,
            username=username,
            key_filename=key_file,
            passphrase=passphrase
        )
    
    def _connect(self):
        """建立连接"""
        # 先尝试密码认证配置
        config = self._get_password_config()
        
        if not config:
            # 再尝试密钥认证配置
            config = self._get_key_config()
        
        if not config:
            QMessageBox.warning(
                self,
                "配置不完整",
                "请填写完整的连接信息"
            )
            return
        
        # 验证密钥文件存在性（如果是密钥认证）
        if hasattr(config, 'key_filename') and config.key_filename:
            if not os.path.exists(config.key_filename):
                QMessageBox.critical(
                    self,
                    "密钥文件不存在",
                    f"找不到密钥文件：{config.key_filename}"
                )
                return
        
        # 获取是否保存密码
        save_password = self.remember_password_checkbox.isChecked()
        
        # 发射连接成功信号
        self.connected.emit(config, save_password)
        self.accept()
    
    def _apply_theme_to_tabs(self):
        """应用主题到标签页"""
        tab_bg = self.get_card_background_color()
        tab_text = self.get_secondary_text_color()
        selected_tab_bg = self.get_background_color()
        selected_tab_text = self.get_accent_color()
        
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.get_color('BORDER')};
                border-radius: 8px;
                background-color: {tab_bg};
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {tab_text};
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 4px;
                font-size: 13px;
                font-weight: 500;
            }}
            
            QTabBar::tab:selected {{
                background-color: {selected_tab_bg};
                color: {selected_tab_text};
                font-weight: 600;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {self.get_color('HOVER')};
            }}
        """)
    
    def _get_secondary_button_style(self) -> str:
        """获取次要按钮样式"""
        bg_color = "#3A3A3C" if self._is_dark_mode else "#F5F5F7"
        text_color = "#F5F5F7" if self._is_dark_mode else "#1D1D1F"
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {"#48484A" if self._is_dark_mode else "#E8E8ED"};
            }}
            
            QPushButton:pressed {{
                background-color: {"#5A5A5C" if self._is_dark_mode else "#D1D1D6"};
            }}
        """
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """主题变化处理"""
        self._apply_theme_to_tabs()
        
        # 更新复选框样式
        self.remember_password_checkbox.setStyleSheet(f"""
            color: {self.get_secondary_text_color()};
            font-size: 13px;
        """)


# 需要导入 os 模块
import os
