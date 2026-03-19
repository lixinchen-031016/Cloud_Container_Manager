"""
容器管理面板模块
显示和管理 Docker 容器
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QMessageBox, QDialog, QTextEdit, QProgressDialog, QApplication,
    QTabWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QAction
from typing import Optional, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssh_client import SSHClient
from core.docker_client import DockerClient, ContainerInfo
from core.deployment_manager import DeploymentManager, ContainerDeployment, PortMapping, VolumeMapping


class ContainerWorker(QThread):
    """容器操作工作线程"""
    
    # 信号定义
    containers_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    operation_completed = pyqtSignal(str)  # 操作完成消息
    
    def __init__(self, docker_client: DockerClient, operation: str, container_id: str = None):
        """
        初始化工作线程
        
        Args:
            docker_client: Docker 客户端
            operation: 操作类型 ("list", "start", "stop", "restart", "remove", "logs")
            container_id: 容器 ID（可选）
        """
        super().__init__()
        self.docker_client = docker_client
        self.operation = operation
        self.container_id = container_id
        self.logs_content = ""
    
    def run(self):
        """执行操作"""
        try:
            if self.operation == "list":
                containers = self.docker_client.list_containers(all=True)
                self.containers_loaded.emit(containers)
            
            elif self.operation == "start":
                success, msg = self.docker_client.start_container(self.container_id)
                if success:
                    self.operation_completed.emit(f"容器 {self.container_id} 已启动")
                else:
                    self.error_occurred.emit(msg)
            
            elif self.operation == "stop":
                success, msg = self.docker_client.stop_container(self.container_id)
                if success:
                    self.operation_completed.emit(f"容器 {self.container_id} 已停止")
                else:
                    self.error_occurred.emit(msg)
            
            elif self.operation == "restart":
                success, msg = self.docker_client.restart_container(self.container_id)
                if success:
                    self.operation_completed.emit(f"容器 {self.container_id} 已重启")
                else:
                    self.error_occurred.emit(msg)
            
            elif self.operation == "remove":
                success, msg = self.docker_client.remove_container(self.container_id, force=True)
                if success:
                    self.operation_completed.emit(f"容器 {self.container_id} 已删除")
                else:
                    self.error_occurred.emit(msg)
            
            elif self.operation == "logs":
                self.logs_content = self.docker_client.get_container_logs(self.container_id, tail=200)
                self.operation_completed.emit("logs_ready")
        
        except Exception as e:
            self.error_occurred.emit(str(e))


class LogsDialog(QDialog):
    """容器日志对话框"""
    
    def __init__(self, container_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"容器日志 - {container_name}")
        self.setMinimumSize(800, 600)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        
        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFontFamily("Courier New")
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_logs)
        btn_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.log_text.clear)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def set_logs(self, content: str):
        """设置日志内容"""
        self.log_text.setPlainText(content)
        # 滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def append_logs(self, content: str):
        """追加日志内容"""
        self.log_text.append(content)
    
    def _refresh_logs(self):
        """刷新日志（由外部触发）"""
        # 这个信号会传递给父窗口处理
        pass


class ContainerManagerPanel(QWidget):
    """容器管理面板"""
    
    # 需要刷新列表的信号
    refresh_needed = pyqtSignal()
    
    def __init__(self, ssh_client: SSHClient, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client
        self.docker_client = DockerClient(ssh_client)
        self.current_worker: Optional[ContainerWorker] = None
        self.logs_dialog: Optional[LogsDialog] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 标题和按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("Docker 容器管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 部署按钮
        self.deploy_btn = QPushButton("🚀 部署容器")
        self.deploy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.deploy_btn.clicked.connect(self._show_deploy_dialog)
        header_layout.addWidget(self.deploy_btn)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_containers)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 说明标签
        info_label = QLabel("右键点击容器可进行操作")
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(info_label)
        
        # 容器表格
        self.container_table = QTableWidget()
        self.container_table.setColumnCount(6)
        self.container_table.setHorizontalHeaderLabels([
            "容器 ID", "名称", "镜像", "状态", "端口", "创建时间"
        ])
        
        # 设置表格属性
        self.container_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.container_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.container_table.setAlternatingRowColors(True)
        self.container_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.container_table.customContextMenuRequested.connect(self._show_context_menu)
        
        # 设置列宽
        header = self.container_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 名称列拉伸
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 镜像列拉伸
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # 创建时间列拉伸
        
        layout.addWidget(self.container_table)
        
        # 状态栏
        self.status_label = QLabel("未加载")
        self.status_label.setStyleSheet("color: #999;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 自动刷新定时器
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh)
    
    def start_monitoring(self):
        """开始监控"""
        print(f"[ContainerManager] 开始监控，SSH 客户端 ID: {id(self.ssh_client)}, 已连接：{self.ssh_client.is_connected}")
        
        if not self.ssh_client.is_connected:
            print(f"[ContainerManager] SSH 未连接")
            self.status_label.setText("未连接")
            return
        
        self.status_label.setText("正在加载容器列表...")
        self.refresh_btn.setEnabled(False)
        
        # 停止之前的监控（如果有）
        self.stop_monitoring()
        
        # 更新 docker_client 的 ssh_client 引用
        if hasattr(self, 'docker_client'):
            self.docker_client.ssh_client = self.ssh_client
        
        # 加载容器列表
        self._load_containers()
        
        # 启动自动刷新（每 10 秒）
        self.auto_refresh_timer.start(10000)
    
    def stop_monitoring(self):
        """停止监控"""
        self.auto_refresh_timer.stop()
        self.status_label.setText("已断开")
        self.refresh_btn.setEnabled(True)
    
    def _load_containers(self):
        """加载容器列表"""
        if not self.ssh_client.is_connected:
            return
        
        self.status_label.setText("加载中...")
        
        # 创建工作线程
        self.current_worker = ContainerWorker(self.docker_client, "list")
        self.current_worker.containers_loaded.connect(self._update_container_table)
        self.current_worker.error_occurred.connect(self._handle_error)
        self.current_worker.start()
    
    def _update_container_table(self, containers: List[ContainerInfo]):
        """更新容器表格"""
        self.container_table.setRowCount(0)  # 清空表格
        
        for container in containers:
            row = self.container_table.rowCount()
            self.container_table.insertRow(row)
            
            # 容器 ID
            id_item = QTableWidgetItem(container.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.container_table.setItem(row, 0, id_item)
            
            # 名称
            name_item = QTableWidgetItem(container.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.container_table.setItem(row, 1, name_item)
            
            # 镜像
            image_item = QTableWidgetItem(container.image)
            image_item.setFlags(image_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.container_table.setItem(row, 2, image_item)
            
            # 状态
            status_item = QTableWidgetItem(container.state)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # 根据状态设置颜色
            if container.state.lower() == "running":
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            else:
                status_item.setBackground(Qt.GlobalColor.gray)
                status_item.setForeground(Qt.GlobalColor.lightGray)
            
            self.container_table.setItem(row, 3, status_item)
            
            # 端口
            ports_item = QTableWidgetItem(container.ports)
            ports_item.setFlags(ports_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.container_table.setItem(row, 4, ports_item)
            
            # 创建时间
            created_item = QTableWidgetItem(container.created)
            created_item.setFlags(created_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.container_table.setItem(row, 5, created_item)
        
        self.status_label.setText(f"共 {len(containers)} 个容器")
        self.refresh_btn.setEnabled(True)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        row = self.container_table.rowAt(pos.y())
        if row < 0:
            return
        
        container_id = self.container_table.item(row, 0).text()
        container_name = self.container_table.item(row, 1).text()
        container_state = self.container_table.item(row, 3).text()
        
        menu = QMenu(self)
        
        # 查看日志
        logs_action = QAction("查看日志", self)
        logs_action.triggered.connect(lambda: self._view_logs(container_id, container_name))
        menu.addAction(logs_action)
        
        menu.addSeparator()
        
        # 根据状态显示不同操作
        if container_state.lower() == "running":
            stop_action = QAction("停止", self)
            stop_action.triggered.connect(lambda: self._stop_container(container_id))
            menu.addAction(stop_action)
            
            restart_action = QAction("重启", self)
            restart_action.triggered.connect(lambda: self._restart_container(container_id))
            menu.addAction(restart_action)
        else:
            start_action = QAction("启动", self)
            start_action.triggered.connect(lambda: self._start_container(container_id))
            menu.addAction(start_action)
        
        menu.addSeparator()
        
        # 删除
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_container(container_id, container_name))
        menu.addAction(delete_action)
        
        menu.exec(self.container_table.viewport().mapToGlobal(pos))
    
    def _view_logs(self, container_id: str, container_name: str):
        """查看容器日志"""
        # 显示加载对话框
        progress = QProgressDialog("正在获取日志...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # 创建工作线程
        self.current_worker = ContainerWorker(self.docker_client, "logs", container_id)
        self.current_worker.operation_completed.connect(
            lambda: self._show_logs_dialog(container_name, progress)
        )
        self.current_worker.error_occurred.connect(
            lambda err: (progress.close(), self._handle_error(err))
        )
        self.current_worker.start()
    
    def _show_logs_dialog(self, container_name: str, progress: QProgressDialog):
        """显示日志对话框"""
        progress.close()
        
        if not self.logs_dialog:
            self.logs_dialog = LogsDialog(container_name, self)
        
        self.logs_dialog.setWindowTitle(f"容器日志 - {container_name}")
        self.logs_dialog.set_logs(self.current_worker.logs_content)
        self.logs_dialog.show()
    
    def _start_container(self, container_id: str):
        """启动容器"""
        if not self._confirm_operation("启动", container_id):
            return
        
        self._execute_operation("start", container_id, "启动中...")
    
    def _stop_container(self, container_id: str):
        """停止容器"""
        if not self._confirm_operation("停止", container_id):
            return
        
        self._execute_operation("stop", container_id, "停止中...")
    
    def _restart_container(self, container_id: str):
        """重启容器"""
        if not self._confirm_operation("重启", container_id):
            return
        
        self._execute_operation("restart", container_id, "重启中...")
    
    def _delete_container(self, container_id: str, container_name: str):
        """删除容器"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除容器 {container_name} ({container_id}) 吗？\n\n此操作不可逆！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._execute_operation("remove", container_id, "删除中...")
    
    def _confirm_operation(self, operation: str, container_id: str) -> bool:
        """确认操作"""
        reply = QMessageBox.question(
            self,
            "确认操作",
            f"确定要{operation}容器 {container_id} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        return reply == QMessageBox.StandardButton.Yes
    
    def _execute_operation(self, operation: str, container_id: str, message: str):
        """执行操作"""
        # 显示进度对话框
        progress = QProgressDialog(message, "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # 创建工作线程
        self.current_worker = ContainerWorker(self.docker_client, operation, container_id)
        self.current_worker.operation_completed.connect(
            lambda msg: (progress.close(), self._handle_operation_result(msg))
        )
        self.current_worker.error_occurred.connect(
            lambda err: (progress.close(), self._handle_error(err))
        )
        self.current_worker.start()
    
    def _handle_operation_result(self, message: str):
        """处理操作结果"""
        if message == "logs_ready":
            return  # 日志已在其他地方处理
        
        QMessageBox.information(self, "操作成功", message)
        # 刷新列表
        QTimer.singleShot(500, self._load_containers)
    
    def _handle_error(self, error: str):
        """处理错误"""
        QMessageBox.critical(self, "操作失败", error)
        self.status_label.setText(f"错误：{error}")
    
    def _auto_refresh(self):
        """自动刷新"""
        if self.ssh_client.is_connected:
            self._load_containers()
    
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_monitoring()
        if self.logs_dialog:
            self.logs_dialog.close()
        super().closeEvent(event)
    
    def _show_deploy_dialog(self):
        """显示部署对话框"""
        dialog = DeployDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 部署成功，刷新列表
            QTimer.singleShot(1000, self._load_containers)


class DeployDialog(QDialog):
    """容器部署对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("部署新容器")
        self.setMinimumSize(600, 700)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 基本信息
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 容器名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：my-nginx")
        form_layout.addRow("容器名称:", self.name_input)
        
        # Docker 镜像
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("例如：nginx:latest")
        form_layout.addRow("Docker 镜像:", self.image_input)
        
        # 重启策略
        self.restart_combo = QComboBox()
        self.restart_combo.addItems(["unless-stopped", "always", "on-failure", "no"])
        form_layout.addRow("重启策略:", self.restart_combo)
        
        layout.addLayout(form_layout)
        
        # 端口映射
        port_group = self._create_port_mapping_group()
        layout.addWidget(port_group)
        
        # 卷映射
        volume_group = self._create_volume_mapping_group()
        layout.addWidget(volume_group)
        
        # 环境变量
        env_group = self._create_env_group()
        layout.addWidget(env_group)
        
        # 高级选项
        advanced_group = self._create_advanced_group()
        layout.addWidget(advanced_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        deploy_btn = QPushButton("部署")
        deploy_btn.setDefault(True)
        deploy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        deploy_btn.clicked.connect(self._deploy)
        btn_layout.addWidget(deploy_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _create_port_mapping_group(self):
        """创建端口映射组"""
        from PyQt6.QtWidgets import QGroupBox
        
        group = QGroupBox("端口映射（可选）")
        layout = QVBoxLayout()
        
        self.ports_layout = QFormLayout()
        layout.addLayout(self.ports_layout)
        
        add_btn = QPushButton("+ 添加端口映射")
        add_btn.clicked.connect(self._add_port_mapping)
        layout.addWidget(add_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_volume_mapping_group(self):
        """创建卷映射组"""
        from PyQt6.QtWidgets import QGroupBox
        
        group = QGroupBox("卷映射（可选）")
        layout = QVBoxLayout()
        
        self.volumes_layout = QFormLayout()
        layout.addLayout(self.volumes_layout)
        
        add_btn = QPushButton("+ 添加卷映射")
        add_btn.clicked.connect(self._add_volume_mapping)
        layout.addWidget(add_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_env_group(self):
        """创建环境变量组"""
        from PyQt6.QtWidgets import QGroupBox
        
        group = QGroupBox("环境变量（可选）")
        layout = QVBoxLayout()
        
        self.env_layout = QFormLayout()
        layout.addLayout(self.env_layout)
        
        add_btn = QPushButton("+ 添加环境变量")
        add_btn.clicked.connect(self._add_env_var)
        layout.addWidget(add_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_advanced_group(self):
        """创建高级选项组"""
        from PyQt6.QtWidgets import QGroupBox
        
        group = QGroupBox("高级选项")
        layout = QFormLayout()
        
        # 启动命令
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("例如：/bin/bash -c 'echo hello'")
        layout.addRow("启动命令:", self.command_input)
        
        # 网络
        self.network_input = QLineEdit()
        self.network_input.setPlaceholderText("例如：bridge, host, none")
        layout.addRow("网络:", self.network_input)
        
        group.setLayout(layout)
        return group
    
    def _add_port_mapping(self):
        """添加端口映射输入框"""
        host_spin = QSpinBox()
        host_spin.setRange(1, 65535)
        host_spin.setValue(80)
        
        container_spin = QSpinBox()
        container_spin.setRange(1, 65535)
        container_spin.setValue(80)
        
        protocol_combo = QComboBox()
        protocol_combo.addItems(["tcp", "udp"])
        
        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(QLabel("主机"))
        widget_layout.addWidget(host_spin)
        widget_layout.addWidget(QLabel("→ 容器"))
        widget_layout.addWidget(container_spin)
        widget_layout.addWidget(protocol_combo)
        widget.setLayout(widget_layout)
        
        self.ports_layout.addRow(widget)
    
    def _add_volume_mapping(self):
        """添加卷映射输入框"""
        host_input = QLineEdit()
        host_input.setPlaceholderText("/host/path")
        
        container_input = QLineEdit()
        container_input.setPlaceholderText("/container/path")
        
        mode_combo = QComboBox()
        mode_combo.addItems(["ro", "rw"])
        
        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(host_input)
        widget_layout.addWidget(QLabel(":"))
        widget_layout.addWidget(container_input)
        widget_layout.addWidget(mode_combo)
        widget.setLayout(widget_layout)
        
        self.volumes_layout.addRow(widget)
    
    def _add_env_var(self):
        """添加环境变量输入框"""
        key_input = QLineEdit()
        key_input.setPlaceholderText("KEY")
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("value")
        
        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(key_input)
        widget_layout.addWidget(QLabel("="))
        widget_layout.addWidget(value_input)
        widget.setLayout(widget_layout)
        
        self.env_layout.addRow(widget)
    
    def _deploy(self):
        """执行部署"""
        # 验证必填字段
        name = self.name_input.text().strip()
        image = self.image_input.text().strip()
        
        if not name or not image:
            QMessageBox.warning(self, "验证失败", "容器名称和镜像是必填项")
            return
        
        # 收集端口映射
        ports = []
        for i in range(self.ports_layout.rowCount()):
            widget = self.ports_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
            if widget and isinstance(widget, QWidget):
                host_spin = widget.findChild(QSpinBox, "", Qt.FindChildOption.FindChildrenRecursively)
                # 简化处理，实际需要更复杂的逻辑来获取值
                pass
        
        # 创建部署配置
        deployment = ContainerDeployment(
            name=name,
            image=image,
            ports=[],  # TODO: 解析端口映射
            volumes=[],  # TODO: 解析卷映射
            environment={},  # TODO: 解析环境变量
            command=self.command_input.text().strip() or None,
            restart_policy=self.restart_combo.currentText(),
            network=self.network_input.text().strip() or None
        )
        
        # 显示进度
        progress = QProgressDialog("正在部署容器...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # 执行部署
        docker_client = self.parent().docker_client
        manager = DeploymentManager(docker_client)
        
        success, message = manager.deploy_container(deployment)
        
        progress.close()
        
        if success:
            QMessageBox.information(self, "部署成功", message)
            self.accept()
        else:
            QMessageBox.critical(self, "部署失败", message)
