"""
服务依赖注入容器
管理服务的生命周期和依赖关系
"""
from typing import Dict, Type, Any, Optional


# 服务类型标识符
SSH_SERVICE = 'ssh_service'
DOCKER_SERVICE = 'docker_service'
CONFIG_SERVICE = 'config_service'


class ServiceContainer:
    """
    服务依赖注入容器
    
    单例模式，管理服务实例的创建和获取
    """
    
    _instance: Optional['ServiceContainer'] = None
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    @classmethod
    def get_instance(cls) -> 'ServiceContainer':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self) -> None:
        """初始化所有服务"""
        if self._initialized:
            return
        
        # 延迟导入，避免循环依赖
        from services.implementations.ssh_service_impl import SSHServiceImpl
        from services.implementations.docker_service_impl import DockerServiceImpl
        from services.implementations.config_service_impl import ConfigServiceImpl
        
        # 注册并初始化服务
        self._services[SSH_SERVICE] = SSHServiceImpl()
        self._services[DOCKER_SERVICE] = DockerServiceImpl()
        self._services[CONFIG_SERVICE] = ConfigServiceImpl()
        
        self._initialized = True
    
    def register(self, name: str, instance: Any) -> None:
        """
        注册服务实例
        
        Args:
            name: 服务名称
            instance: 服务实例
        """
        self._services[name] = instance
    
    def resolve(self, name: str) -> Any:
        """
        解析服务实例
        
        Args:
            name: 服务名称
            
        Returns:
            服务实例
        """
        if not self._initialized:
            self.initialize()
        
        service = self._services.get(name)
        if service is None:
            raise ValueError(f"未找到服务实现：{name}")
        return service
    
    def reset(self) -> None:
        """重置容器（用于测试）"""
        self._services.clear()
        self._initialized = False
