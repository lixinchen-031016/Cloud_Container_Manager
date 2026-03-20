"""
SSH 服务接口定义
"""
from abc import abstractmethod
from typing import Optional, Callable, List, Protocol
from core.ssh_client import SSHConfig


class ISSHService(Protocol):
    """SSH 服务接口 - 封装 SSH 连接和管理功能"""
    
    def connect(self, config: SSHConfig) -> tuple[bool, str]:
        """连接到服务器"""
        ...
    
    def disconnect(self) -> None:
        """断开当前连接"""
        ...
    
    def exec_command(self, command: str, timeout: int = 10) -> tuple[int, str, str]:
        """执行命令"""
        ...
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        ...
    
    def get_current_config(self) -> Optional[SSHConfig]:
        """获取当前连接配置"""
        ...
    
    def on_connection_status_changed(self, callback: Callable[[bool], None]) -> None:
        """注册连接状态变化回调"""
        ...
