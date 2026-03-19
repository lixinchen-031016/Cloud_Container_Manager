"""
SSH 连接对话框模块
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTabWidget, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssh_client import SSHConfig


class ConnectionDialog(QDialog):
    """SSH 连接配置对话框"""
    
    # 连接成功信号
    connected = pyqtSignal(SSHConfig, bool)  # 新增：是否保存密码
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接到服务器")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 创建标签页（密码认证 / 密钥认证）
        tabs = QTabWidget()
        
        # 密码认证页面
        password_widget = self._create_password_auth_page()
        tabs.addTab(password_widget, "密码认证")
        
        # 密钥认证页面
        key_widget = self._create_key_auth_page()
        tabs.addTab(key_widget, "密钥认证")
        
        layout.addWidget(tabs)
        
        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self._test_connection)
        layout.addWidget(test_btn)
        
        # 记住密码选项
        self.remember_password_checkbox = QCheckBox("记住密码（加密存储）")
        self.remember_password_checkbox.setChecked(False)
        layout.addWidget(self.remember_password_checkbox)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        connect_btn = QPushButton("连接")
        connect_btn.setDefault(True)
        connect_btn.clicked.connect(self._connect)
        btn_layout.addWidget(connect_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _create_password_auth_page(self) -> QWidget:
        """创建密码认证页面"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # 主机
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("例如：192.168.1.100 或 example.com")
        layout.addRow("主机:", self.host_input)
        
        # 端口
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        layout.addRow("端口:", self.port_input)
        
        # 用户名
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("例如：root")
        layout.addRow("用户名:", self.username_input)
        
        # 密码
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("密码:", self.password_input)
        
        widget.setLayout(layout)
        return widget
    
    def _create_key_auth_page(self) -> QWidget:
        """创建密钥认证页面"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # 主机
        self.key_host_input = QLineEdit()
        self.key_host_input.setPlaceholderText("例如：192.168.1.100 或 example.com")
        layout.addRow("主机:", self.key_host_input)
        
        # 端口
        self.key_port_input = QSpinBox()
        self.key_port_input.setRange(1, 65535)
        self.key_port_input.setValue(22)
        layout.addRow("端口:", self.key_port_input)
        
        # 用户名
        self.key_username_input = QLineEdit()
        self.key_username_input.setPlaceholderText("例如：root")
        layout.addRow("用户名:", self.key_username_input)
        
        # 密钥文件
        key_file_layout = QHBoxLayout()
        self.key_file_input = QLineEdit()
        self.key_file_input.setPlaceholderText("~/.ssh/id_rsa")
        key_file_layout.addWidget(self.key_file_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_key_file)
        key_file_layout.addWidget(browse_btn)
        
        layout.addRow("密钥文件:", key_file_layout)
        
        # 密钥密码（可选）
        self.key_passphrase_input = QLineEdit()
        self.key_passphrase_input.setPlaceholderText("如果密钥有密码则填写")
        self.key_passphrase_input.setEchoMode(QLineEdit.EchoMode.Password)
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
    
    def _test_connection(self):
        """测试连接"""
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
        
        # 显示加载状态
        QMessageBox.information(
            self,
            "测试中",
            "正在测试连接，请稍候..."
        )
        
        # 执行连接测试
        from core.ssh_client import SSHClient
        
        client = SSHClient()
        success, message = client.connect(config)
        client.disconnect()
        
        if success:
            QMessageBox.information(
                self,
                "连接成功",
                f"可以连接到 {config.hostname}"
            )
        else:
            QMessageBox.critical(
                self,
                "连接失败",
                message
            )
    
    def _connect(self):
        """建立连接"""
        # 先尝试密码认证配置
        config = self._get_password_config()
        auth_type = "password"
        
        if not config:
            # 再尝试密钥认证配置
            config = self._get_key_config()
            auth_type = "key"
        
        if not config:
            QMessageBox.warning(
                self,
                "配置不完整",
                "请填写完整的连接信息"
            )
            return
        
        # 验证密钥文件存在性（如果是密钥认证）
        if auth_type == "key" and not os.path.exists(config.key_filename):
            QMessageBox.critical(
                self,
                "密钥文件不存在",
                f"找不到密钥文件：{config.key_filename}"
            )
            return
        
        # 获取是否保存密码
        save_password = self.remember_password_checkbox.isChecked()
        
        # 发射连接成功信号（包含是否保存密码的标志）
        self.connected.emit(config, save_password)
        self.accept()
