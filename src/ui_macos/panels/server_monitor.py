"""
macOS 风格服务器监控面板模块
显示 CPU、内存、磁盘、网络等系统资源使用情况
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint
from PyQt6.QtGui import QColor

from typing import Optional, List
from services.interfaces.i_ssh_service import ISSHService
from services.alert_manager import get_alert_manager
from ui_macos.widgets.themed_widget import ThemedWidget
from ui_macos.widgets.macos_card import MacOsCard, MacOsProgressBar
from ui_macos.widgets.macos_button import MacOsButton
from utils.system_parser import SystemParser


class MonitorWorker(QThread):
    """监控数据获取工作线程"""
    
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ssh_service: ISSHService):
        super().__init__()
        self.ssh_service = ssh_service
        self.running = True
    
    def run(self):
        """执行监控任务"""
        while self.running and self.ssh_service.is_connected():
            try:
                if not self.ssh_service.is_connected():
                    break
                
                data = self._collect_monitor_data()
                self.data_updated.emit(data)
            except Exception as e:
                self.error_occurred.emit(str(e))
            
            self.msleep(2000)
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()
    
    def _collect_monitor_data(self) -> dict:
        """收集所有监控数据"""
        data = {}
        
        try:
            # CPU 信息
            exit_code, cpu_output, _ = self.ssh_service.exec_command("cat /proc/cpuinfo", timeout=5)
            data['cpu_info'] = SystemParser.parse_cpu_info(cpu_output)
            
            # CPU 使用率
            exit_code, top_output, _ = self.ssh_service.exec_command("top -bn1 | head -n 5", timeout=5)
            if data.get('cpu_info'):
                data['cpu_info'].usage_percent = SystemParser.parse_top_cpu(top_output)
            
            # 内存信息
            exit_code, mem_output, _ = self.ssh_service.exec_command("free -k", timeout=5)
            data['memory'] = SystemParser.parse_memory_info(mem_output)
            
            # 磁盘信息
            exit_code, disk_output, _ = self.ssh_service.exec_command("df -k", timeout=5)
            data['disks'] = SystemParser.parse_disk_info(disk_output)
            
            # 网络信息
            exit_code, net_output, _ = self.ssh_service.exec_command("cat /proc/net/dev", timeout=5)
            data['networks'] = SystemParser.parse_network_info(net_output)
            
            # 系统负载
            exit_code, uptime_output, _ = self.ssh_service.exec_command("uptime", timeout=5)
            data['load'] = SystemParser.parse_system_load(uptime_output)
            
        except Exception as e:
            raise
        
        return data


class ServerMonitorPanel(ThemedWidget):
    """macOS 风格服务器监控面板"""
    
    def __init__(self, ssh_service: ISSHService, parent=None):
        super().__init__(parent)
        self.ssh_service = ssh_service
        self.worker: Optional[MonitorWorker] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和刷新按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 服务器监控")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.get_text_color()};
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_btn = MacOsButton("⟳ 刷新", is_primary=False)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self._manual_refresh)
        self.refresh_btn.setFixedWidth(100)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        # 内容 widget
        content_widget = ThemedWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # CPU 卡片
        self.cpu_card = MacOsCard("CPU")
        self.cpu_usage_bar = MacOsProgressBar(0.0, 100.0)
        self.cpu_usage_bar.set_dark_mode(self._is_dark_mode)
        self.cpu_card.add_content_widget(self.cpu_usage_bar)
        
        self.cpu_value_label = QLabel("0%")
        self.cpu_value_label.setStyleSheet(f"""
            color: {self.get_accent_color()};
            font-size: 28px;
            font-weight: 600;
            margin-top: 8px;
        """)
        self.cpu_card.add_content_widget(self.cpu_value_label)
        
        self.cpu_cores_label = QLabel("核心数：-")
        self.cpu_cores_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.cpu_card.add_content_widget(self.cpu_cores_label)
        
        self.cpu_model_label = QLabel("型号：-")
        self.cpu_model_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.cpu_card.add_content_widget(self.cpu_model_label)
        
        grid_layout.addWidget(self.cpu_card, 0, 0)
        
        # 内存卡片
        self.memory_card = MacOsCard("内存")
        self.memory_usage_bar = MacOsProgressBar(0.0, 100.0)
        self.memory_usage_bar.set_dark_mode(self._is_dark_mode)
        self.memory_card.add_content_widget(self.memory_usage_bar)
        
        self.memory_value_label = QLabel("0%")
        self.memory_value_label.setStyleSheet(f"""
            color: {self.get_accent_color()};
            font-size: 28px;
            font-weight: 600;
            margin-top: 8px;
        """)
        self.memory_card.add_content_widget(self.memory_value_label)
        
        self.memory_detail_label = QLabel("")
        self.memory_detail_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.memory_card.add_content_widget(self.memory_detail_label)
        
        grid_layout.addWidget(self.memory_card, 0, 1)
        
        # 系统负载卡片
        self.load_card = MacOsCard("系统负载")
        self.load_value_label = QLabel("-")
        self.load_value_label.setStyleSheet(f"""
            color: {self.get_accent_color()};
            font-size: 28px;
            font-weight: 600;
            margin-top: 8px;
        """)
        self.load_card.add_content_widget(self.load_value_label)
        
        self.load_1min_label = QLabel("1 分钟：-")
        self.load_1min_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.load_card.add_content_widget(self.load_1min_label)
        
        self.load_5min_label = QLabel("5 分钟：-")
        self.load_5min_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.load_card.add_content_widget(self.load_5min_label)
        
        self.load_15min_label = QLabel("15 分钟：-")
        self.load_15min_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.load_card.add_content_widget(self.load_15min_label)
        
        self.processes_label = QLabel("进程数：-/-")
        self.processes_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.load_card.add_content_widget(self.processes_label)
        
        grid_layout.addWidget(self.load_card, 1, 0)
        
        # 网络卡片
        self.network_card = MacOsCard("网络流量")
        self.network_label = QLabel("等待数据...")
        self.network_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 13px;")
        self.network_card.add_content_widget(self.network_label)
        grid_layout.addWidget(self.network_card, 1, 1)
        
        # 磁盘卡片（跨两列）
        self.disk_card = MacOsCard("磁盘空间")
        self.disk_layout = QVBoxLayout()
        self.disk_layout.setSpacing(10)
        self.disk_layout.setContentsMargins(0, 0, 0, 0)
        self.disk_card.add_content_widget(QWidget_wrapper(self.disk_layout))
        grid_layout.addWidget(self.disk_card, 2, 0, 1, 2)
        
        content_widget.setLayout(grid_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # 状态标签
        self.status_label = QLabel("● 未连接")
        self.status_label.setStyleSheet(f"""
            color: {self.get_secondary_text_color()};
            font-size: 13px;
            padding: 10px 0;
        """)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 自动刷新定时器
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh)
    
    def start_monitoring(self):
        """开始监控"""
        if not self.ssh_service.is_connected():
            self.status_label.setText("未连接")
            return
        
        self.status_label.setText("正在连接...")
        self.refresh_btn.setEnabled(False)
        
        # 停止之前的监控
        self.stop_monitoring()
        
        # 启动工作线程
        self.worker = MonitorWorker(self.ssh_service)
        self.worker.data_updated.connect(self._update_display)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.start()
        
        # 启动自动刷新定时器
        self.auto_refresh_timer.start(5000)
    
    def stop_monitoring(self):
        """停止监控"""
        if self.worker:
            self.worker.stop()
            self.worker = None
        
        self.auto_refresh_timer.stop()
        self.status_label.setText("已断开")
        self.refresh_btn.setEnabled(True)
    
    def _manual_refresh(self):
        """手动刷新"""
        if self.worker and self.worker.isRunning():
            self.status_label.setText("刷新中...")
        else:
            self._auto_refresh()
    
    def _auto_refresh(self):
        """自动刷新"""
        if not self.ssh_service.is_connected():
            return
        
        try:
            if self.worker:
                data = self.worker._collect_monitor_data()
                self._update_display(data)
        except Exception as e:
            self._handle_error(str(e))
    
    def _update_display(self, data: dict):
        """更新显示数据"""
        self.status_label.setText("● 已连接 • 实时更新中")
        self.status_label.setStyleSheet(f"""
            color: #34C759;
            font-size: 13px;
            padding: 10px 0;
        """)
        
        # 获取告警管理器
        alert_manager = get_alert_manager()
        server_name = self.ssh_service.get_current_config().hostname if self.ssh_service.get_current_config() else "服务器"
        
        # 更新 CPU
        if 'cpu_info' in data and data['cpu_info']:
            cpu = data['cpu_info']
            usage = cpu.usage_percent or 0.0
            self.cpu_usage_bar.set_value(usage)
            self.cpu_value_label.setText(f"{usage:.1f}%")
            self.cpu_cores_label.setText(f"核心数：{cpu.cores}")
            self.cpu_model_label.setText(f"型号：{cpu.model or 'Unknown'}")
            
            # 检查告警
            alert_manager.check_and_alert(server_name, cpu_usage=usage)
        
        # 更新内存
        if 'memory' in data and data['memory']:
            mem = data['memory']
            usage = mem.usage_percent or 0.0
            self.memory_usage_bar.set_value(usage)
            self.memory_value_label.setText(f"{usage:.1f}%")
            
            total_str = SystemParser.format_size(mem.total)
            used_str = SystemParser.format_size(mem.used)
            available_str = SystemParser.format_size(mem.available)
            
            self.memory_detail_label.setText(
                f"总计：{total_str} | 已用：{used_str} | 可用：{available_str}"
            )
            
            # 检查告警
            alert_manager.check_and_alert(server_name, memory_usage=usage)
        
        # 更新系统负载
        if 'load' in data and data['load']:
            load = data['load']
            self.load_value_label.setText(f"{load.load_1min:.2f}")
            self.load_1min_label.setText(f"1 分钟：{load.load_1min:.2f}")
            self.load_5min_label.setText(f"5 分钟：{load.load_5min:.2f}")
            self.load_15min_label.setText(f"15 分钟：{load.load_15min:.2f}")
            self.processes_label.setText(
                f"进程数：{load.running_processes}/{load.total_processes}"
            )
        
        # 更新磁盘
        if 'disks' in data and data['disks']:
            # 检查根分区磁盘告警
            for disk in data['disks']:
                if disk.mount_point == '/':
                    alert_manager.check_and_alert(server_name, disk_usage=disk.usage_percent)
                    break
        
        # 更新网络
        if 'networks' in data and data['networks']:
            networks = data['networks']
            network_text = ""
            for net in networks[:3]:
                rx_gb = net.bytes_received / (1024**3)
                tx_gb = net.bytes_sent / (1024**3)
                network_text += f"{net.interface}: ↓{rx_gb:.2f} GB ↑{tx_gb:.2f} GB\n"
            
            self.network_label.setText(network_text.strip() if network_text.strip() else "暂无数据")
        
        # 更新磁盘
        if 'disks' in data and data['disks']:
            # 清空现有布局
            while self.disk_layout.count():
                item = self.disk_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            disks = data['disks']
            important_disks = [d for d in disks if d.mount_point in ['/', '/home', '/data']]
            other_disks = [d for d in disks if d.mount_point not in ['/', '/home', '/data']]
            
            for disk in important_disks + other_disks[:3]:
                disk_widget = self._create_disk_row(disk)
                self.disk_layout.addWidget(disk_widget)
    
    def _create_disk_row(self, disk) -> QWidget:
        """创建磁盘行控件"""
        widget = ThemedWidget()
        layout = QHBoxLayout()
        
        mount_label = QLabel(disk.mount_point)
        mount_label.setMinimumWidth(80)
        mount_label.setStyleSheet(f"color: {self.get_text_color()}; font-size: 13px;")
        layout.addWidget(mount_label)
        
        progress = MacOsProgressBar(disk.used, disk.total)
        progress.set_dark_mode(self._is_dark_mode)
        layout.addWidget(progress)
        
        size_label = QLabel(
            f"{SystemParser.format_size(disk.used)} / {SystemParser.format_size(disk.total)}"
        )
        size_label.setStyleSheet(f"color: {self.get_secondary_text_color()}; font-size: 12px;")
        layout.addWidget(size_label)
        
        widget.setLayout(layout)
        return widget
    
    def _handle_error(self, error: str):
        """处理错误"""
        self.status_label.setText(f"错误：{error}")
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """主题变化处理"""
        # 更新所有卡片的主题
        for card in [self.cpu_card, self.memory_card, self.load_card, 
                     self.network_card, self.disk_card]:
            card.set_dark_mode(is_dark_mode)
        
        # 更新进度条主题
        self.cpu_usage_bar.set_dark_mode(is_dark_mode)
        self.memory_usage_bar.set_dark_mode(is_dark_mode)
        
        # 更新标签颜色
        title_color = self.get_text_color()
        secondary_color = self.get_secondary_text_color()
        accent_color = self.get_accent_color()
        
        self.cpu_value_label.setStyleSheet(f"""
            color: {accent_color};
            font-size: 28px;
            font-weight: 600;
            margin-top: 8px;
        """)
        
        self.memory_value_label.setStyleSheet(f"""
            color: {accent_color};
            font-size: 28px;
            font-weight: 600;
            margin-top: 8px;
        """)
        
        self.load_value_label.setStyleSheet(f"""
            color: {accent_color};
            font-size: 28px;
            font-weight: 600;
            margin-top: 8px;
        """)


class QWidget_wrapper(QWidget):
    """QWidget 包装器，用于添加 QVBoxLayout 到卡片"""
    def __init__(self, layout):
        super().__init__()
        self.setLayout(layout)
