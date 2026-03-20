"""
服务器监控面板模块
显示 CPU、内存、磁盘、网络等系统资源使用情况
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QProgressBar, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ssh_client import SSHClient
from utils.system_parser import (
    SystemParser, CPUInfo, MemoryInfo, DiskInfo, NetworkInfo, SystemLoad
)


class MonitorWorker(QThread):
    """监控数据获取工作线程"""
    
    # 数据更新信号
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ssh_client: SSHClient):
        super().__init__()
        self.ssh_client = ssh_client
        self.running = True
    
    def run(self):
        """执行监控任务"""
        print(f"[MonitorWorker] 开始运行，SSH 客户端对象 ID: {id(self.ssh_client)}")
        
        while self.running and self.ssh_client.is_connected:
            try:
                # 每次循环前检查连接状态
                if not self.ssh_client.is_connected:
                    print("[MonitorWorker] SSH 连接已断开，停止监控")
                    break
                
                data = self._collect_monitor_data()
                self.data_updated.emit(data)
            except Exception as e:
                print(f"[MonitorWorker] 错误：{e}")
                import traceback
                traceback.print_exc()
                self.error_occurred.emit(str(e))
            
            # 每 2 秒更新一次
            self.msleep(2000)
        
        print("[MonitorWorker] 线程结束")
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()
    
    def _collect_monitor_data(self) -> dict:
        """收集所有监控数据"""
        data = {}
        
        try:
            # CPU 信息
            exit_code, cpu_output, error = self.ssh_client.exec_command("cat /proc/cpuinfo", timeout=5)
            print(f"[DEBUG] CPU 输出长度：{len(cpu_output) if cpu_output else 0}, 退出码：{exit_code}")
            data['cpu_info'] = SystemParser.parse_cpu_info(cpu_output)
            
            # CPU 使用率（通过 top）
            exit_code, top_output, error = self.ssh_client.exec_command(
                "top -bn1 | head -n 5", timeout=5
            )
            print(f"[DEBUG] TOP 输出长度：{len(top_output) if top_output else 0}, 退出码：{exit_code}")
            if data['cpu_info']:
                data['cpu_info'].usage_percent = SystemParser.parse_top_cpu(top_output)
            
            # 内存信息
            exit_code, mem_output, error = self.ssh_client.exec_command("free -k", timeout=5)
            print(f"[DEBUG] MEM 输出长度：{len(mem_output) if mem_output else 0}, 退出码：{exit_code}")
            data['memory'] = SystemParser.parse_memory_info(mem_output)
            
            # 磁盘信息
            exit_code, disk_output, error = self.ssh_client.exec_command("df -k", timeout=5)
            print(f"[DEBUG] DISK 输出长度：{len(disk_output) if disk_output else 0}, 退出码：{exit_code}")
            data['disks'] = SystemParser.parse_disk_info(disk_output)
            
            # 网络信息
            exit_code, net_output, error = self.ssh_client.exec_command("cat /proc/net/dev", timeout=5)
            print(f"[DEBUG] NET 输出长度：{len(net_output) if net_output else 0}, 退出码：{exit_code}")
            data['networks'] = SystemParser.parse_network_info(net_output)
            
            # 系统负载
            exit_code, uptime_output, error = self.ssh_client.exec_command("uptime", timeout=5)
            print(f"[DEBUG] UPTIME 输出长度：{len(uptime_output) if uptime_output else 0}, 退出码：{exit_code}")
            data['load'] = SystemParser.parse_system_load(uptime_output)
            
        except Exception as e:
            print(f"[ERROR] 收集监控数据失败：{e}")
            import traceback
            traceback.print_exc()
            raise
        
        return data


class ResourceCard(QFrame):
    """资源卡片组件 - macOS 风格"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("resourceCard")
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-weight: 600;
            font-size: 15px;
            color: #1d1d1f;
        """)
        layout.addWidget(self.title_label)
        
        # 内容区域
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)
        
        # 应用卡片样式
        self.setStyleSheet("""
            QFrame#resourceCard {
                background-color: #ffffff;
                border-radius: 12px;
            }
            
            QFrame#resourceCard:hover {
                background-color: #fafafa;
            }
        """)
    
    def add_progress_bar(self, label: str, value: float = 0.0) -> QProgressBar:
        """添加进度条"""
        # 标签
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            color: #86868b;
            font-size: 13px;
            margin-bottom: 4px;
        """)
        
        # 进度条
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(value))
        progress.setFormat(f"{value:.1f}%")
        progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 根据值设置颜色
        if value >= 90:
            color = "#ff3b30"  # 红色 - 危险
        elif value >= 70:
            color = "#ff9500"  # 橙色 - 警告
        else:
            color = "#007aff"  # 蓝色 - 正常
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: center;
                background-color: #e8e8ed;
                height: 6px;
                font-size: 11px;
                color: transparent;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        
        self.content_layout.addWidget(label_widget)
        self.content_layout.addWidget(progress)
        
        return progress
    
    def add_value_label(self, text: str) -> QLabel:
        """添加数值标签"""
        label = QLabel(text)
        label.setStyleSheet("""
            color: #1d1d1f;
            font-size: 24px;
            font-weight: 600;
            margin-top: 4px;
        """)
        self.content_layout.addWidget(label)
        return label
    
    def add_info_label(self, text: str) -> QLabel:
        """添加信息标签"""
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("""
            color: #86868b;
            font-size: 12px;
            line-height: 1.4;
        """)
        self.content_layout.addWidget(label)
        return label


class ServerMonitorPanel(QWidget):
    """服务器监控面板"""
    
    def __init__(self, ssh_client: SSHClient, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client
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
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #1d1d1f;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("⟳ 刷新")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self._manual_refresh)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        # 内容 widget
        content_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # CPU 卡片
        self.cpu_card = ResourceCard("CPU")
        self.cpu_usage_bar = self.cpu_card.add_progress_bar("使用率", 0.0)
        self.cpu_value_label = self.cpu_card.add_value_label("0%")
        self.cpu_cores_label = self.cpu_card.add_info_label("核心数：-")
        self.cpu_model_label = self.cpu_card.add_info_label("型号：-")
        grid_layout.addWidget(self.cpu_card, 0, 0)
        
        # 内存卡片
        self.memory_card = ResourceCard("内存")
        self.memory_usage_bar = self.memory_card.add_progress_bar("使用率", 0.0)
        self.memory_value_label = self.memory_card.add_value_label("0%")
        self.memory_detail_label = self.memory_card.add_info_label("")
        grid_layout.addWidget(self.memory_card, 0, 1)
        
        # 系统负载卡片
        self.load_card = ResourceCard("系统负载")
        self.load_value_label = self.load_card.add_value_label("-")
        self.load_1min_label = self.load_card.add_info_label("1 分钟：-")
        self.load_5min_label = self.load_card.add_info_label("5 分钟：-")
        self.load_15min_label = self.load_card.add_info_label("15 分钟：-")
        self.processes_label = self.load_card.add_info_label("进程数：-/-")
        grid_layout.addWidget(self.load_card, 1, 0)
        
        # 网络卡片
        self.network_card = ResourceCard("网络流量")
        self.network_label = self.network_card.add_info_label("等待数据...")
        grid_layout.addWidget(self.network_card, 1, 1)
        
        # 磁盘卡片（跨两列）
        self.disk_card = ResourceCard("磁盘空间")
        self.disk_layout = QVBoxLayout()
        self.disk_layout.setSpacing(10)
        self.disk_layout.setContentsMargins(0, 0, 0, 0)
        self.disk_card.content_layout.addLayout(self.disk_layout)
        grid_layout.addWidget(self.disk_card, 2, 0, 1, 2)
        
        content_widget.setLayout(grid_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # 状态标签
        self.status_label = QLabel("● 未连接")
        self.status_label.setStyleSheet("""
            color: #86868b;
            font-size: 13px;
            padding: 10px;
        """)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 自动刷新定时器
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh)
    
    def start_monitoring(self):
        """开始监控"""
        print(f"[ServerMonitor] 开始监控，SSH 客户端 ID: {id(self.ssh_client)}, 已连接：{self.ssh_client.is_connected}")
        
        if not self.ssh_client.is_connected:
            print(f"[ServerMonitor] SSH 未连接，停止监控")
            self.status_label.setText("未连接")
            return
        
        self.status_label.setText("正在连接...")
        self.refresh_btn.setEnabled(False)
        
        # 先停止之前的监控（如果有）
        self.stop_monitoring()
        
        # 启动工作线程
        print(f"[ServerMonitor] 创建新的 MonitorWorker")
        self.worker = MonitorWorker(self.ssh_client)
        self.worker.data_updated.connect(self._update_display)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.start()
        
        # 同时启动自动刷新定时器作为备用
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
        """自动刷新（备用机制）"""
        if not self.ssh_client.is_connected:
            return
        
        try:
            # 直接获取一次数据
            data = self.worker._collect_monitor_data() if self.worker else {}
            self._update_display(data)
        except Exception as e:
            self._handle_error(str(e))
    
    def _update_display(self, data: dict):
        """更新显示数据"""
        self.status_label.setText("● 已连接 • 实时更新中")
        self.status_label.setStyleSheet("color: #34c759; font-size: 13px; padding: 10px;")
        
        # 更新 CPU
        if 'cpu_info' in data and data['cpu_info']:
            cpu = data['cpu_info']
            usage = cpu.usage_percent or 0.0
            self.cpu_usage_bar.setValue(int(usage))
            self.cpu_usage_bar.setFormat(f"{usage:.1f}%")
            self.cpu_value_label.setText(f"{usage:.1f}%")
            self.cpu_cores_label.setText(f"核心数：{cpu.cores}")
            self.cpu_model_label.setText(f"型号：{cpu.model or 'Unknown'}")
        
        # 更新内存
        if 'memory' in data and data['memory']:
            mem = data['memory']
            usage = mem.usage_percent or 0.0
            self.memory_usage_bar.setValue(int(usage))
            self.memory_usage_bar.setFormat(f"{usage:.1f}%")
            self.memory_value_label.setText(f"{usage:.1f}%")
            
            total_str = SystemParser.format_size(mem.total)
            used_str = SystemParser.format_size(mem.used)
            available_str = SystemParser.format_size(mem.available)
            
            self.memory_detail_label.setText(
                f"总计：{total_str} | 已用：{used_str} | 可用：{available_str}"
            )
        
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
        
        # 更新网络
        if 'networks' in data and data['networks']:
            networks = data['networks']
            network_text = ""
            for net in networks[:3]:  # 只显示前 3 个网卡
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
            # 优先显示根分区和其他重要挂载点
            important_disks = [d for d in disks if d.mount_point in ['/', '/home', '/data']]
            other_disks = [d for d in disks if d.mount_point not in ['/', '/home', '/data']]
            
            for disk in important_disks + other_disks[:3]:  # 最多显示 5 个
                disk_widget = QWidget()
                disk_layout = QHBoxLayout()
                
                mount_label = QLabel(disk.mount_point)
                mount_label.setMinimumWidth(80)
                disk_layout.addWidget(mount_label)
                
                progress = QProgressBar()
                progress.setRange(0, 100)
                progress.setValue(int(disk.usage_percent))
                progress.setFormat(f"{disk.usage_percent:.0f}%")
                
                # 根据使用率设置颜色
                if disk.usage_percent < 60:
                    color = "#4CAF50"
                elif disk.usage_percent < 80:
                    color = "#FF9800"
                else:
                    color = "#F44336"
                
                progress.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        text-align: center;
                        min-width: 100px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                    }}
                """)
                disk_layout.addWidget(progress)
                
                size_label = QLabel(
                    f"{SystemParser.format_size(disk.used)} / {SystemParser.format_size(disk.total)}"
                )
                disk_layout.addWidget(size_label)
                
                disk_widget.setLayout(disk_layout)
                self.disk_layout.addWidget(disk_widget)
    
    def _handle_error(self, error: str):
        """处理错误"""
        self.status_label.setText(f"错误：{error}")
        print(f"[监控错误] {error}")
        import traceback
        traceback.print_exc()
    
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_monitoring()
        super().closeEvent(event)
