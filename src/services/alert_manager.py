"""
服务器告警管理器
监控服务器资源使用并在超过阈值时发送通知
"""
from typing import Dict, Optional, Callable
from services.notification_service import get_notification_service


class AlertManager:
    """
    服务器告警管理器
    
    功能：
    - 监控 CPU、内存、磁盘使用率
    - 设置自定义阈值
    - 发送通知告警
    - 防止告警风暴（冷却时间）
    """
    
    _instance: Optional['AlertManager'] = None
    
    def __new__(cls) -> 'AlertManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.notification_service = get_notification_service()
        
        # 告警阈值（百分比）
        self.cpu_threshold = 90.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        
        # 冷却时间（秒）- 防止告警风暴
        self.cooldown_period = 300  # 5 分钟
        
        # 上次告警时间
        self._last_alert_time: Dict[str, float] = {}
        
        # 告警回调
        self._alert_callbacks: list = []
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'AlertManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_threshold(
        self,
        cpu: float = None,
        memory: float = None,
        disk: float = None
    ) -> None:
        """
        设置告警阈值
        
        Args:
            cpu: CPU 使用率阈值（0-100）
            memory: 内存使用率阈值（0-100）
            disk: 磁盘使用率阈值（0-100）
        """
        if cpu is not None:
            self.cpu_threshold = max(0, min(100, cpu))
        if memory is not None:
            self.memory_threshold = max(0, min(100, memory))
        if disk is not None:
            self.disk_threshold = max(0, min(100, disk))
    
    def check_and_alert(
        self,
        server_name: str,
        cpu_usage: float = None,
        memory_usage: float = None,
        disk_usage: float = None
    ) -> None:
        """
        检查资源使用并发送告警
        
        Args:
            server_name: 服务器名称
            cpu_usage: CPU 使用率
            memory_usage: 内存使用率
            disk_usage: 磁盘使用率
        """
        import time
        current_time = time.time()
        
        # 检查 CPU
        if cpu_usage is not None and cpu_usage >= self.cpu_threshold:
            alert_key = f"{server_name}_cpu"
            if self._should_send_alert(alert_key, current_time):
                self.notification_service.send_server_alert(
                    server_name, "CPU", cpu_usage, self.cpu_threshold
                )
                self._last_alert_time[alert_key] = current_time
                self._notify_callbacks(server_name, "CPU", cpu_usage)
        
        # 检查内存
        if memory_usage is not None and memory_usage >= self.memory_threshold:
            alert_key = f"{server_name}_memory"
            if self._should_send_alert(alert_key, current_time):
                self.notification_service.send_server_alert(
                    server_name, "内存", memory_usage, self.memory_threshold
                )
                self._last_alert_time[alert_key] = current_time
                self._notify_callbacks(server_name, "Memory", memory_usage)
        
        # 检查磁盘
        if disk_usage is not None and disk_usage >= self.disk_threshold:
            alert_key = f"{server_name}_disk"
            if self._should_send_alert(alert_key, current_time):
                self.notification_service.send_server_alert(
                    server_name, "磁盘", disk_usage, self.disk_threshold
                )
                self._last_alert_time[alert_key] = current_time
                self._notify_callbacks(server_name, "Disk", disk_usage)
    
    def _should_send_alert(self, alert_key: str, current_time: float) -> bool:
        """
        判断是否应该发送告警（检查冷却时间）
        
        Args:
            alert_key: 告警键
            current_time: 当前时间戳
            
        Returns:
            是否应该发送告警
        """
        last_time = self._last_alert_time.get(alert_key, 0)
        return (current_time - last_time) >= self.cooldown_period
    
    def _notify_callbacks(
        self,
        server_name: str,
        resource_type: str,
        value: float
    ) -> None:
        """通知所有注册的回调"""
        for callback in self._alert_callbacks:
            try:
                callback(server_name, resource_type, value)
            except Exception as e:
                print(f"[AlertManager] 通知回调失败：{e}")
    
    def on_alert(self, callback: Callable[[str, str, float], None]) -> None:
        """
        注册告警回调
        
        Args:
            callback: 回调函数，参数为 (server_name, resource_type, value)
        """
        self._alert_callbacks.append(callback)
    
    def send_connection_lost(self, server_name: str) -> None:
        """
        发送连接丢失通知
        
        Args:
            server_name: 服务器名称
        """
        self.notification_service.send_connection_lost(server_name)
    
    def send_deployment_complete(
        self,
        container_name: str,
        success: bool,
        message: str = ""
    ) -> None:
        """
        发送部署完成通知
        
        Args:
            container_name: 容器名称
            success: 是否成功
            message: 附加消息
        """
        self.notification_service.send_deployment_complete(
            container_name, success, message
        )


# 全局告警管理器实例
_global_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """获取全局告警管理器实例"""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager.get_instance()
    return _global_alert_manager
