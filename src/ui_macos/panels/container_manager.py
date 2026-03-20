"""
macOS 风格容器管理面板模块
显示和管理 Docker 容器
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QMessageBox, QDialog, QTextEdit, QProgressDialog, QApplication,
    QTabWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox, QFileDialog,
    QGroupBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QColor

from typing import Optional, List
from services.interfaces.i_docker_service import IDockerService
from ui_macos.widgets.themed_widget import ThemedWidget
from ui_macos.widgets.macos_button import MacOsButton
from ui_macos.widgets.macos_card import MacOsCard
from core.docker_client import DockerClient, ContainerInfo


class ContainerManagerPanel(ThemedWidget):
    """macOS 风格容器管理面板"""
    
    def __init__(self, docker_service: IDockerService, parent=None):
        super().__init__(parent)
        self.docker_service = docker_service
        self.logs_dialog: Optional[LogsDialog] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("🐳 容器管理")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.get_text_color()};
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 部署按钮
        self.deploy_btn = MacOsButton("🚀 部署容器", is_primary=True)
        self.deploy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.deploy_btn.clicked.connect(self._show_deploy_dialog)
        header_layout.addWidget(self.deploy_btn)
        
        # 刷新按钮
        self.refresh_btn = MacOsButton("⟳ 刷新", is_primary=False)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self._load_containers)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 说明标签
        info_label = QLabel("右键点击容器可进行操作")
        info_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        layout.addWidget(info_label)
        
        # 容器表格
        self.container_table = self._create_table()
        layout.addWidget(self.container_table)
        
        # 状态栏
        self.status_label = QLabel("未加载")
        self.status_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 自动刷新定时器
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh)
    
    def _create_table(self) -> QTableWidget:
        """创建容器表格"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "容器 ID", "名称", "镜像", "状态", "端口", "创建时间"
        ])
        
        # 设置表格属性
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)
        
        # 设置列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        # 应用主题样式
        self._apply_table_theme(table)
        
        return table
    
    def _apply_table_theme(self, table: QTableWidget):
        """应用主题到表格"""
        bg_color = self.get_card_background_color()
        alternate_bg = "#3A3A3C" if self._is_dark_mode else "#FAFAFA"
        header_bg = "#3A3A3C" if self._is_dark_mode else "#F5F5F7"
        border_color = self.get_color('BORDER')
        gridline_color = "#3A3A3C" if self._is_dark_mode else "#F5F5F7"
        selected_bg = "rgba(10, 132, 255, 0.2)" if self._is_dark_mode else "#E8F2FF"
        selected_text = self.get_accent_color()
        header_text = self.get_secondary_text_color()
        
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {border_color};
                border-radius: 8px;
                gridline-color: {gridline_color};
                background-color: {bg_color};
                alternate-background-color: {alternate_bg};
            }}
            
            QTableWidget::item {{
                padding: 10px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {selected_bg};
                color: {selected_text};
            }}
            
            QHeaderView::section {{
                background-color: {header_bg};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {border_color};
                font-weight: 600;
                color: {header_text};
                font-size: 12px;
                text-transform: uppercase;
            }}
        """)
    
    def start_monitoring(self):
        """开始监控"""
        self.status_label.setText("正在加载容器列表...")
        self.refresh_btn.setEnabled(False)
        
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
        try:
            containers = self.docker_service.list_containers(all=True)
            self._update_container_table(containers)
        except Exception as e:
            self._handle_error(str(e))
    
    def _update_container_table(self, containers: List[ContainerInfo]):
        """更新容器表格"""
        self.container_table.setRowCount(0)
        
        for container in containers:
            row = self.container_table.rowCount()
            self.container_table.insertRow(row)
            
            # 容器 ID
            id_item = QTableWidgetItem(container.id[:12])
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
                # 运行中：使用浅绿色背景 + 深绿色文字（浅色模式）或亮绿色背景 + 白色文字（深色模式）
                bg_color = self._get_running_color()
                if not self._is_dark_mode:
                    # 浅色模式：浅绿色背景 + 深绿色文字
                    status_item.setBackground(bg_color)
                    status_item.setForeground(QColor("#006400"))  # 深绿色
                else:
                    # 深色模式：亮绿色背景 + 白色文字
                    status_item.setBackground(bg_color)
                    status_item.setForeground(Qt.GlobalColor.white)
            else:
                # 已停止：灰色背景 + 白色/深灰色文字
                bg_color = self._get_stopped_color()
                status_item.setBackground(bg_color)
                if not self._is_dark_mode:
                    status_item.setForeground(QColor("#505050"))  # 深灰色
                else:
                    status_item.setForeground(QColor("#A0A0A0"))  # 浅灰色
            
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
    
    def _get_running_color(self):
        """获取运行中颜色"""
        from PyQt6.QtGui import QColor
        return QColor("#34C759" if not self._is_dark_mode else "#30D158")
    
    def _get_stopped_color(self):
        """获取已停止颜色"""
        from PyQt6.QtGui import QColor
        return QColor("#8E8E93" if not self._is_dark_mode else "#48484A")
    
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
        progress = QProgressDialog("正在获取日志...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            logs_content = self.docker_service.get_container_logs(container_id, tail=200)
            progress.close()
            
            if not self.logs_dialog:
                self.logs_dialog = LogsDialog(container_name, self)
            
            self.logs_dialog.setWindowTitle(f"容器日志 - {container_name}")
            self.logs_dialog.set_logs(logs_content)
            self.logs_dialog.show()
        except Exception as e:
            progress.close()
            self._handle_error(str(e))
    
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
        try:
            if operation == "start":
                success, msg = self.docker_service.start_container(container_id)
            elif operation == "stop":
                success, msg = self.docker_service.stop_container(container_id)
            elif operation == "restart":
                success, msg = self.docker_service.restart_container(container_id)
            elif operation == "remove":
                success, msg = self.docker_service.remove_container(container_id, force=True)
            else:
                return
            
            if success:
                QMessageBox.information(self, "操作成功", msg)
                QTimer.singleShot(500, self._load_containers)
            else:
                QMessageBox.critical(self, "操作失败", msg)
        except Exception as e:
            self._handle_error(str(e))
    
    def _handle_error(self, error: str):
        """处理错误"""
        QMessageBox.critical(self, "操作失败", error)
        self.status_label.setText(f"错误：{error}")
    
    def _auto_refresh(self):
        """自动刷新"""
        self._load_containers()
    
    def _show_deploy_dialog(self):
        """显示部署对话框"""
        dialog = DeployDialog(self, self.docker_service)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QTimer.singleShot(1000, self._load_containers)
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """主题变化处理"""
        self._apply_table_theme(self.container_table)


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
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _refresh_logs(self):
        """刷新日志"""
        pass


class DeployDialog(QDialog):
    """容器部署对话框"""
    
    def __init__(self, parent=None, docker_service: IDockerService = None):
        super().__init__(parent)
        self.docker_service = docker_service
        self.setWindowTitle("部署新容器")
        self.setMinimumSize(600, 700)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("🚀 部署新容器")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #1d1d1f;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # 基本信息
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 容器名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：my-nginx")
        self.name_input.setFixedHeight(36)
        form_layout.addRow("容器名称:", self.name_input)
        
        # Docker 镜像
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("例如：nginx:latest")
        self.image_input.setFixedHeight(36)
        form_layout.addRow("Docker 镜像:", self.image_input)
        
        # 重启策略
        self.restart_combo = QComboBox()
        self.restart_combo.addItems(["unless-stopped", "always", "on-failure", "no"])
        self.restart_combo.setFixedHeight(36)
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
        
        deploy_btn = MacOsButton("部署", is_primary=True)
        deploy_btn.clicked.connect(self._deploy)
        btn_layout.addWidget(deploy_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _create_port_mapping_group(self):
        """创建端口映射组"""
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
        group = QGroupBox("高级选项")
        layout = QFormLayout()
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("例如：/bin/bash -c 'echo hello'")
        self.command_input.setFixedHeight(36)
        layout.addRow("启动命令:", self.command_input)
        
        self.network_input = QLineEdit()
        self.network_input.setPlaceholderText("例如：bridge, host, none")
        self.network_input.setFixedHeight(36)
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
        host_input.setFixedHeight(32)
        
        container_input = QLineEdit()
        container_input.setPlaceholderText("/container/path")
        container_input.setFixedHeight(32)
        
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
        key_input.setFixedHeight(32)
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("value")
        value_input.setFixedHeight(32)
        
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
        name = self.name_input.text().strip()
        image = self.image_input.text().strip()
        
        if not name or not image:
            QMessageBox.warning(self, "验证失败", "容器名称和镜像是必填项")
            return
        
        # TODO: 收集端口映射、卷映射、环境变量
        # 简化版本，只部署基本配置
        
        progress = QProgressDialog("正在部署容器...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            # 使用 docker run 命令部署
            from core.deployment_manager import DeploymentManager, ContainerDeployment
            from core.docker_client import DockerClient
            
            deployment = ContainerDeployment(
                name=name,
                image=image,
                ports=[],
                volumes=[],
                environment={},
                command=self.command_input.text().strip() or None,
                restart_policy=self.restart_combo.currentText(),
                network=self.network_input.text().strip() or None
            )
            
            # 获取底层 Docker 客户端
            docker_client = self.docker_service.get_client()
            if not docker_client:
                raise Exception("无法获取 Docker 客户端")
            
            manager = DeploymentManager(docker_client)
            success, message = manager.deploy_container(deployment)
            
            progress.close()
            
            if success:
                QMessageBox.information(self, "部署成功", message)
                self.accept()
            else:
                QMessageBox.critical(self, "部署失败", message)
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "部署失败", str(e))
