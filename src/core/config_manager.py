"""
服务器配置管理模块
保存和加载服务器连接配置
"""
import json
import os
from typing import List, Dict, Optional
from dataclasses import asdict

from core.ssh_client import SSHConfig
from core.password_manager import encrypt_password, decrypt_password


class ConfigManager:
    """服务器配置管理器"""
    
    def __init__(self):
        self.config_file = os.path.expanduser("~/.cloud_container_manager/servers.json")
        self.servers: List[Dict] = []
        self._load_config()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, mode=0o700)  # 仅所有者可读写
    
    def _load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.servers = json.load(f)
            else:
                self.servers = []
        except Exception as e:
            print(f"加载配置失败：{e}")
            self.servers = []
    
    def _save_config(self):
        """保存配置"""
        try:
            self._ensure_config_dir()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.servers, f, indent=2, ensure_ascii=False)
            # 设置文件权限为仅所有者可读写
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            print(f"保存配置失败：{e}")
    
    def add_server(self, config: SSHConfig, name: Optional[str] = None, save_password: bool = False):
        """
        添加服务器配置
        
        Args:
            config: SSH 配置
            name: 服务器名称（可选）
            save_password: 是否保存密码
        """
        server_data = {
            'name': name or f"{config.username}@{config.hostname}",
            'hostname': config.hostname,
            'port': config.port,
            'username': config.username,
            'auth_type': 'password' if config.password else 'key',
            'save_password': save_password,
        }
        
        # 如果选择保存密码，则加密存储
        if save_password and config.password:
            server_data['encrypted_password'] = encrypt_password(config.password)
        elif 'encrypted_password' in server_data:
            del server_data['encrypted_password']
        
        # 如果是密钥认证，保存密钥文件路径（不加密，因为密钥文件本身已有权限保护）
        if config.key_filename:
            server_data['key_filename'] = config.key_filename
            if config.passphrase:
                # 保存密钥密码（加密）
                server_data['encrypted_passphrase'] = encrypt_password(config.passphrase)
        
        self.servers.append(server_data)
        self._save_config()
    
    def update_server(self, index: int, config: SSHConfig, save_password: bool = False):
        """更新服务器配置"""
        if 0 <= index < len(self.servers):
            old_data = self.servers[index]
            server_data = {
                'name': old_data.get('name', f"{config.username}@{config.hostname}"),
                'hostname': config.hostname,
                'port': config.port,
                'username': config.username,
                'auth_type': 'password' if config.password else 'key',
                'save_password': save_password,
            }
            
            if save_password and config.password:
                server_data['encrypted_password'] = encrypt_password(config.password)
            
            if config.key_filename:
                server_data['key_filename'] = config.key_filename
                if config.passphrase:
                    server_data['encrypted_passphrase'] = encrypt_password(config.passphrase)
            
            self.servers[index] = server_data
            self._save_config()
    
    def remove_server(self, index: int):
        """删除服务器配置"""
        if 0 <= index < len(self.servers):
            del self.servers[index]
            self._save_config()
    
    def get_servers(self) -> List[Dict]:
        """获取所有服务器配置"""
        return self.servers
    
    def get_server_config(self, index: int) -> Optional[SSHConfig]:
        """获取服务器配置（包含解密的密码）"""
        if 0 <= index < len(self.servers):
            data = self.servers[index]
            
            password = None
            passphrase = None
            key_filename = data.get('key_filename')
            
            # 解密密码
            if data.get('save_password') and 'encrypted_password' in data:
                password = decrypt_password(data['encrypted_password'])
            
            # 解密密钥密码
            if 'encrypted_passphrase' in data:
                passphrase = decrypt_password(data['encrypted_passphrase'])
            
            # 如果没有保存任何认证信息，返回 None
            if not password and not key_filename:
                return None
            
            return SSHConfig(
                hostname=data['hostname'],
                port=data['port'],
                username=data['username'],
                password=password,
                key_filename=key_filename,
                passphrase=passphrase
            )
        
        return None
    
    def clear_servers(self):
        """清空所有服务器配置"""
        self.servers = []
        self._save_config()
