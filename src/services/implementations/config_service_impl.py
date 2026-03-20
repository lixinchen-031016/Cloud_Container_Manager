"""
配置服务实现
封装现有的 ConfigManager
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Optional, Dict, Any
from core.config_manager import ConfigManager
from core.ssh_client import SSHConfig
from services.interfaces.i_config_service import IConfigService


class ConfigServiceImpl(IConfigService):
    """
    配置服务实现
    
    复用现有的 ConfigManager，提供配置管理功能
    """
    
    def __init__(self):
        self._manager = ConfigManager()
    
    def add_server(self, config: SSHConfig, save_password: bool = False) -> bool:
        """添加服务器配置"""
        try:
            self._manager.add_server(config, save_password=save_password)
            return True
        except Exception as e:
            print(f"[ConfigService] 添加服务器失败：{e}")
            return False
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """获取所有服务器配置"""
        try:
            return self._manager.get_servers()
        except Exception as e:
            print(f"[ConfigService] 获取服务器列表失败：{e}")
            return []
    
    def get_server_config(self, index: int) -> Optional[SSHConfig]:
        """获取指定服务器的配置（包含解密的密码）"""
        try:
            return self._manager.get_server_config(index)
        except Exception as e:
            print(f"[ConfigService] 获取服务器配置失败：{e}")
            return None
    
    def update_server(self, index: int, config: SSHConfig, save_password: bool = False) -> bool:
        """更新服务器配置"""
        try:
            self._manager.update_server(index, config, save_password=save_password)
            return True
        except Exception as e:
            print(f"[ConfigService] 更新服务器配置失败：{e}")
            return False
    
    def remove_server(self, index: int) -> bool:
        """删除服务器配置"""
        try:
            self._manager.remove_server(index)
            return True
        except Exception as e:
            print(f"[ConfigService] 删除服务器配置失败：{e}")
            return False
    
    def get_manager(self) -> ConfigManager:
        """获取底层配置管理器（用于兼容现有代码）"""
        return self._manager
