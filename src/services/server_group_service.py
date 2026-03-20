"""
服务器分组管理模块
支持多服务器配置分组和标签管理
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ServerGroup:
    """服务器分组数据模型"""
    
    def __init__(
        self,
        id: str = None,
        name: str = "",
        color: str = "#007AFF",
        server_ids: List[str] = None,
        created_at: str = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.color = color
        self.server_ids = server_ids or []
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'server_ids': self.server_ids,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServerGroup':
        """从字典创建"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            color=data.get('color', '#007AFF'),
            server_ids=data.get('server_ids', []),
            created_at=data.get('created_at')
        )


class ManagedServer:
    """托管服务器数据模型"""
    
    def __init__(
        self,
        id: str = None,
        name: str = "",
        group_id: str = None,
        tags: List[str] = None,
        hostname: str = "",
        username: str = "",
        port: int = 22,
        sort_order: int = 0,
        created_at: str = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.group_id = group_id
        self.tags = tags or []
        self.hostname = hostname
        self.username = username
        self.port = port
        self.sort_order = sort_order
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'group_id': self.group_id,
            'tags': self.tags,
            'hostname': self.hostname,
            'username': self.username,
            'port': self.port,
            'sort_order': self.sort_order,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ManagedServer':
        """从字典创建"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            group_id=data.get('group_id'),
            tags=data.get('tags', []),
            hostname=data.get('hostname', ''),
            username=data.get('username', ''),
            port=data.get('port', 22),
            sort_order=data.get('sort_order', 0),
            created_at=data.get('created_at')
        )


class ServerGroupService:
    """
    服务器分组管理服务
    
    功能：
    - 创建、编辑、删除分组
    - 添加、移除服务器到分组
    - 标签管理
    - 数据持久化
    """
    
    _instance: Optional['ServerGroupService'] = None
    CONFIG_FILE = os.path.expanduser("~/.cloud_container_manager/groups.json")
    
    def __new__(cls) -> 'ServerGroupService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._groups: List[ServerGroup] = []
        self._servers: List[ManagedServer] = []
        
        # 加载配置
        self._load_config()
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'ServerGroupService':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载分组
                self._groups = [ServerGroup.from_dict(g) for g in data.get('groups', [])]
                
                # 加载服务器
                self._servers = [ManagedServer.from_dict(s) for s in data.get('servers', [])]
                
                print(f"[ServerGroupService] 已加载 {len(self._groups)} 个分组，{len(self._servers)} 个服务器")
        except Exception as e:
            print(f"[ServerGroupService] 加载配置失败：{e}")
            self._groups = []
            self._servers = []
    
    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            
            data = {
                'groups': [g.to_dict() for g in self._groups],
                'servers': [s.to_dict() for s in self._servers]
            }
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"[ServerGroupService] 已保存配置")
        except Exception as e:
            print(f"[ServerGroupService] 保存配置失败：{e}")
    
    # ========== 分组管理 ==========
    
    def create_group(self, name: str, color: str = "#007AFF") -> ServerGroup:
        """
        创建分组
        
        Args:
            name: 分组名称
            color: 分组颜色
            
        Returns:
            创建的分组对象
        """
        group = ServerGroup(name=name, color=color)
        self._groups.append(group)
        self._save_config()
        return group
    
    def update_group(self, group_id: str, name: str = None, color: str = None) -> bool:
        """
        更新分组
        
        Args:
            group_id: 分组 ID
            name: 新名称
            color: 新颜色
            
        Returns:
            是否成功
        """
        for group in self._groups:
            if group.id == group_id:
                if name:
                    group.name = name
                if color:
                    group.color = color
                self._save_config()
                return True
        return False
    
    def delete_group(self, group_id: str) -> bool:
        """
        删除分组
        
        Args:
            group_id: 分组 ID
            
        Returns:
            是否成功
        """
        for i, group in enumerate(self._groups):
            if group.id == group_id:
                # 将该分组的服务器移到未分组
                for server in self._servers:
                    if server.group_id == group_id:
                        server.group_id = None
                
                del self._groups[i]
                self._save_config()
                return True
        return False
    
    def get_groups(self) -> List[ServerGroup]:
        """获取所有分组"""
        return self._groups
    
    def get_group(self, group_id: str) -> Optional[ServerGroup]:
        """获取指定分组"""
        for group in self._groups:
            if group.id == group_id:
                return group
        return None
    
    # ========== 服务器管理 ==========
    
    def add_server_to_group(
        self,
        group_id: str,
        name: str,
        hostname: str,
        username: str,
        port: int = 22,
        tags: List[str] = None
    ) -> ManagedServer:
        """
        添加服务器到分组
        
        Args:
            group_id: 分组 ID
            name: 服务器名称
            hostname: 主机名
            username: 用户名
            port: 端口
            tags: 标签列表
            
        Returns:
            创建的服务器对象
        """
        server = ManagedServer(
            name=name,
            group_id=group_id,
            tags=tags or [],
            hostname=hostname,
            username=username,
            port=port
        )
        self._servers.append(server)
        
        # 更新分组的服务器列表
        group = self.get_group(group_id)
        if group:
            group.server_ids.append(server.id)
        
        self._save_config()
        return server
    
    def remove_server_from_group(self, server_id: str) -> bool:
        """
        从分组移除服务器
        
        Args:
            server_id: 服务器 ID
            
        Returns:
            是否成功
        """
        for i, server in enumerate(self._servers):
            if server.id == server_id:
                # 从分组中移除
                group = self.get_group(server.group_id)
                if group and server.id in group.server_ids:
                    group.server_ids.remove(server.id)
                
                del self._servers[i]
                self._save_config()
                return True
        return False
    
    def move_server_to_group(self, server_id: str, new_group_id: str) -> bool:
        """
        移动服务器到另一个分组
        
        Args:
            server_id: 服务器 ID
            new_group_id: 新分组 ID
            
        Returns:
            是否成功
        """
        for server in self._servers:
            if server.id == server_id:
                # 从旧分组移除
                old_group = self.get_group(server.group_id)
                if old_group and server.id in old_group.server_ids:
                    old_group.server_ids.remove(server.id)
                
                # 添加到新分组
                server.group_id = new_group_id
                new_group = self.get_group(new_group_id)
                if new_group:
                    new_group.server_ids.append(server.id)
                
                self._save_config()
                return True
        return False
    
    def get_servers_in_group(self, group_id: str) -> List[ManagedServer]:
        """获取分组中的所有服务器"""
        return [s for s in self._servers if s.group_id == group_id]
    
    def get_ungrouped_servers(self) -> List[ManagedServer]:
        """获取未分组的服务器"""
        return [s for s in self._servers if s.group_id is None]
    
    def get_server(self, server_id: str) -> Optional[ManagedServer]:
        """获取指定服务器"""
        for server in self._servers:
            if server.id == server_id:
                return server
        return None
    
    # ========== 标签管理 ==========
    
    def add_tag_to_server(self, server_id: str, tag: str) -> bool:
        """
        添加标签到服务器
        
        Args:
            server_id: 服务器 ID
            tag: 标签
            
        Returns:
            是否成功
        """
        for server in self._servers:
            if server.id == server_id:
                if tag not in server.tags:
                    server.tags.append(tag)
                    self._save_config()
                return True
        return False
    
    def remove_tag_from_server(self, server_id: str, tag: str) -> bool:
        """
        从服务器移除标签
        
        Args:
            server_id: 服务器 ID
            tag: 标签
            
        Returns:
            是否成功
        """
        for server in self._servers:
            if server.id == server_id:
                if tag in server.tags:
                    server.tags.remove(tag)
                    self._save_config()
                return True
        return False
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for server in self._servers:
            tags.update(server.tags)
        return sorted(list(tags))
    
    def search_by_tag(self, tag: str) -> List[ManagedServer]:
        """根据标签搜索服务器"""
        return [s for s in self._servers if tag in s.tags]


# 全局服务实例
_global_server_group_service: Optional[ServerGroupService] = None


def get_server_group_service() -> ServerGroupService:
    """获取全局服务器分组服务实例"""
    global _global_server_group_service
    if _global_server_group_service is None:
        _global_server_group_service = ServerGroupService.get_instance()
    return _global_server_group_service
