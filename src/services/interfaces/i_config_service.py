"""
配置服务接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.ssh_client import SSHConfig


class IConfigService(ABC):
    """配置服务接口 - 封装服务器配置管理功能"""
    
    @abstractmethod
    def add_server(self, config: SSHConfig, save_password: bool = False) -> bool:
        """
        添加服务器配置
        
        Args:
            config: SSH 配置
            save_password: 是否保存密码
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def get_servers(self) -> List[Dict[str, Any]]:
        """
        获取所有服务器配置
        
        Returns:
            服务器配置列表
        """
        pass
    
    @abstractmethod
    def get_server_config(self, index: int) -> Optional[SSHConfig]:
        """
        获取指定服务器的配置（包含解密的密码）
        
        Args:
            index: 服务器索引
            
        Returns:
            SSH 配置，如果不存在则返回 None
        """
        pass
    
    @abstractmethod
    def update_server(self, index: int, config: SSHConfig, save_password: bool = False) -> bool:
        """
        更新服务器配置
        
        Args:
            index: 服务器索引
            config: 新的 SSH 配置
            save_password: 是否保存密码
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def remove_server(self, index: int) -> bool:
        """
        删除服务器配置
        
        Args:
            index: 服务器索引
            
        Returns:
            是否成功
        """
        pass
