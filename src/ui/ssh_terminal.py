"""
SSH 终端模拟器模块
提供简单的终端界面
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssh_client import SSHClient


class TerminalWorker(QThread):
    """终端命令执行工作线程"""
    
    output_received = pyqtSignal(str)
    command_completed = pyqtSignal()
    
    def __init__(self, ssh_client: SSHClient, command: str):
        super().__init__()
        self.ssh_client = ssh_client
        self.command = command
    
    def run(self):
        """执行命令"""
        try:
            if not self.ssh_client.is_connected:
                self.output_received.emit("[错误] 未连接到服务器\n")
                return
            
            # 执行命令
            exit_code, output, error = self.ssh_client.exec_command(self.command, timeout=30)
            
            if output:
                self.output_received.emit(output)
            
            if error:
                self.output_received.emit(f"[错误] {error}")
            
            self.command_completed.emit()
            
        except Exception as e:
            self.output_received.emit(f"[异常] {str(e)}\n")
            self.command_completed.emit()


class SSHTerminal(QWidget):
    """SSH 终端模拟器"""
    
    def __init__(self, ssh_client: SSHClient, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client
        self.current_worker = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 终端输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFontFamily("Courier New")
        self.output_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 13px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 5px;
            }
        """)
        layout.addWidget(self.output_text)
        
        # 命令输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        
        # 提示符
        self.prompt_label = QLabel("$")
        self.prompt_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-weight: bold;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
        """)
        input_layout.addWidget(self.prompt_label)
        
        # 命令输入框
        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("""
            QLineEdit {
                font-family: 'Courier New', monospace;
                font-size: 13px;
                padding: 5px;
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
            }
        """)
        self.command_input.setPlaceholderText("输入命令...")
        self.command_input.returnPressed.connect(self._execute_command)
        input_layout.addWidget(self.command_input)
        
        # 执行按钮
        self.exec_btn = QPushButton("执行")
        self.exec_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        self.exec_btn.clicked.connect(self._execute_command)
        input_layout.addWidget(self.exec_btn)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # 显示欢迎信息
        self._show_welcome_message()
    
    def _show_welcome_message(self):
        """显示欢迎信息"""
        welcome = """====================================
SSH Terminal
====================================
提示:
- 输入命令后按 Enter 执行
- 支持所有标准 Linux 命令
- 输入 'exit' 或 'quit' 关闭终端
====================================

"""
        self.output_text.append(welcome)
        self._update_prompt()
    
    def _update_prompt(self):
        """更新命令提示符"""
        if self.ssh_client.is_connected and self.ssh_client.config:
            username = self.ssh_client.config.username
            hostname = self.ssh_client.config.hostname
            self.prompt_label.setText(f"{username}@{hostname}$")
        else:
            self.prompt_label.setText("$")
    
    def _execute_command(self):
        """执行命令"""
        command = self.command_input.text().strip()
        
        if not command:
            return
        
        # 处理退出命令
        if command.lower() in ('exit', 'quit'):
            self.close()
            return
        
        # 显示执行的命令
        prompt = self.prompt_label.text()
        self.output_text.append(f"\n{prompt} {command}\n")
        
        # 清空输入框
        self.command_input.clear()
        
        # 禁用输入
        self._set_input_enabled(False)
        
        # 创建工作线程执行命令
        self.current_worker = TerminalWorker(self.ssh_client, command)
        self.current_worker.output_received.connect(self._append_output)
        self.current_worker.command_completed.connect(self._on_command_completed)
        self.current_worker.start()
    
    def _append_output(self, text: str):
        """追加输出"""
        self.output_text.append(text)
        # 滚动到底部
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _on_command_completed(self):
        """命令执行完成"""
        self._set_input_enabled(True)
        self.command_input.setFocus()
    
    def _set_input_enabled(self, enabled: bool):
        """设置输入是否可用"""
        self.command_input.setEnabled(enabled)
        self.exec_btn.setEnabled(enabled)
        if enabled:
            self.command_input.setFocus()
    
    def connect_to_server(self, ssh_client: SSHClient):
        """连接到服务器"""
        self.ssh_client = ssh_client
        self._update_prompt()
        
        if self.ssh_client.is_connected:
            self.output_text.append("\n[已连接]\n")
        else:
            self.output_text.append("\n[未连接]\n")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.wait()
        super().closeEvent(event)
