"""
SSH 服务实现
封装现有的 SSHClient，提供异步支持
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Optional, Callable, List
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from core.ssh_client import SSHClient, SSHConfig


class SSHConnectionWorker(QThread):
    """SSH 连接工作线程"""
    connection_ready = pyqtSignal(bool, str)
    
    def __init__(self, ssh_client: SSHClient, config: SSHConfig):
        super().__init__()
        self.ssh_client = ssh_client
        self.config = config
    
    def run(self):
        """执行连接"""
        try:
            success, message = self.ssh_client.connect(self.config)
            self.connection_ready.emit(success, message)
        except Exception as e:
            self.connection_ready.emit(False, str(e))


class SSHServiceImpl(QObject):
    """
    SSH 服务实现
    
    复用现有的 SSHClient，添加异步连接支持和状态管理
    """
    
    # 连接状态变化信号
    connection_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        QObject.__init__(self)
        self._client = SSHClient()
        self._current_config: Optional[SSHConfig] = None
        self._status_callbacks: List[Callable[[bool], None]] = []
        self._connection_worker: Optional[SSHConnectionWorker] = None
        
        # 连接信号到槽
        self._setup_connections()
    
    def _setup_connections(self):
        """设置信号连接"""
        # 内部使用，暂不实现复杂逻辑
    
    def connect(self, config: SSHConfig) -> tuple[bool, str]:
        """
        连接到服务器（同步版本）
        
        Args:
            config: SSH 配置
            
        Returns:
            (success, message)
        """
        success, message = self._client.connect(config)
        if success:
            self._current_config = config
            self.connection_status_changed.emit(True)
            self._notify_status_callbacks(True)
        return success, message
    
    def connect_async(self, config: SSHConfig) -> None:
        """
        异步连接到服务器
        
        Args:
            config: SSH 配置
        """
        if self._connection_worker and self._connection_worker.isRunning():
            self._connection_worker.wait()
        
        self._connection_worker = SSHConnectionWorker(self._client, config)
        self._connection_worker.connection_ready.connect(self._on_connection_completed)
        self._connection_worker.start()
    
    def _on_connection_completed(self, success: bool, message: str):
        """连接完成回调"""
        if success:
            self._current_config = self._connection_worker.config
            self.connection_status_changed.emit(True)
            self._notify_status_callbacks(True)
    
    def disconnect(self) -> None:
        """断开连接"""
        self._client.disconnect()
        self._current_config = None
        self.connection_status_changed.emit(False)
        self._notify_status_callbacks(False)
    
    def exec_command(self, command: str, timeout: int = 10) -> tuple[int, str, str]:
        """执行命令"""
        if not self._client.is_connected:
            return -1, "", "未连接到服务器"
        
        return self._client.exec_command(command, timeout)
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._client.is_connected
    
    def get_current_config(self) -> Optional[SSHConfig]:
        """获取当前连接配置"""
        return self._current_config
    
    def on_connection_status_changed(self, callback: Callable[[bool], None]) -> None:
        """注册连接状态变化回调"""
        self._status_callbacks.append(callback)
    
    def _notify_status_callbacks(self, connected: bool) -> None:
        """通知所有状态回调"""
        for callback in self._status_callbacks:
            try:
                callback(connected)
            except Exception as e:
                print(f"[SSHService] 通知回调失败：{e}")
    
    def get_client(self) -> SSHClient:
        """获取底层 SSH 客户端（用于兼容现有代码）"""
        return self._client
