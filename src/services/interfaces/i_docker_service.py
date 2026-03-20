"""
Docker 服务接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from core.docker_client import ContainerInfo


class IDockerService(ABC):
    """Docker 服务接口 - 封装 Docker 容器管理功能"""
    
    @abstractmethod
    def list_containers(self, all: bool = False) -> List[ContainerInfo]:
        """
        列出容器
        
        Args:
            all: 是否包含所有容器（包括已停止的）
            
        Returns:
            容器信息列表
        """
        pass
    
    @abstractmethod
    def start_container(self, container_id: str) -> tuple[bool, str]:
        """
        启动容器
        
        Args:
            container_id: 容器 ID
            
        Returns:
            (success, message)
        """
        pass
    
    @abstractmethod
    def stop_container(self, container_id: str) -> tuple[bool, str]:
        """
        停止容器
        
        Args:
            container_id: 容器 ID
            
        Returns:
            (success, message)
        """
        pass
    
    @abstractmethod
    def restart_container(self, container_id: str) -> tuple[bool, str]:
        """
        重启容器
        
        Args:
            container_id: 容器 ID
            
        Returns:
            (success, message)
        """
        pass
    
    @abstractmethod
    def remove_container(self, container_id: str, force: bool = False) -> tuple[bool, str]:
        """
        删除容器
        
        Args:
            container_id: 容器 ID
            force: 是否强制删除
            
        Returns:
            (success, message)
        """
        pass
    
    @abstractmethod
    def get_container_logs(self, container_id: str, tail: int = 200) -> str:
        """
        获取容器日志
        
        Args:
            container_id: 容器 ID
            tail: 显示最后多少行
            
        Returns:
            日志内容
        """
        pass
    
    @abstractmethod
    def get_container_stats(self, container_id: str) -> dict:
        """
        获取容器资源统计
        
        Args:
            container_id: 容器 ID
            
        Returns:
            资源统计信息
        """
        pass
