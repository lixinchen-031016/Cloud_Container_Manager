"""
Docker 服务实现
封装现有的 DockerClient，提供异步支持
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from core.docker_client import DockerClient, ContainerInfo


class DockerOperationWorker(QThread):
    """Docker 操作工作线程"""
    operation_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, docker_client: DockerClient, operation: str, *args, **kwargs):
        super().__init__()
        self.docker_client = docker_client
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """执行操作"""
        try:
            result = self._execute_operation()
            self.operation_completed.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _execute_operation(self):
        """执行具体操作"""
        if self.operation == "list_containers":
            return self.docker_client.list_containers(*self.args, **self.kwargs)
        elif self.operation == "start_container":
            return self.docker_client.start_container(*self.args, **self.kwargs)
        elif self.operation == "stop_container":
            return self.docker_client.stop_container(*self.args, **self.kwargs)
        elif self.operation == "restart_container":
            return self.docker_client.restart_container(*self.args, **self.kwargs)
        elif self.operation == "remove_container":
            return self.docker_client.remove_container(*self.args, **self.kwargs)
        elif self.operation == "get_logs":
            return self.docker_client.get_container_logs(*self.args, **self.kwargs)
        elif self.operation == "get_stats":
            return self.docker_client.get_container_stats(*self.args, **self.kwargs)
        else:
            raise ValueError(f"未知操作：{self.operation}")


class DockerServiceImpl(QObject):
    """
    Docker 服务实现
    
    复用现有的 DockerClient，添加异步操作支持
    """
    
    def __init__(self, ssh_client=None):
        QObject.__init__(self)
        self._ssh_client = ssh_client
        self._docker_client = DockerClient(ssh_client) if ssh_client else None
        self._current_worker: Optional[DockerOperationWorker] = None
    
    def set_ssh_client(self, ssh_client) -> None:
        """设置 SSH 客户端（用于更新连接）"""
        self._ssh_client = ssh_client
        if ssh_client:
            self._docker_client = DockerClient(ssh_client)
    
    def list_containers(self, all: bool = False) -> List[ContainerInfo]:
        """列出容器（同步版本）"""
        if not self._docker_client:
            return []
        return self._docker_client.list_containers(all=all)
    
    def list_containers_async(self, all: bool = False, callback=None) -> None:
        """异步列出容器"""
        if not self._docker_client:
            if callback:
                callback([])
            return
        
        self._current_worker = DockerOperationWorker(
            self._docker_client, "list_containers", all=all
        )
        if callback:
            self._current_worker.operation_completed.connect(callback)
        self._current_worker.start()
    
    def start_container(self, container_id: str) -> tuple[bool, str]:
        """启动容器（同步版本）"""
        if not self._docker_client:
            return False, "未初始化 Docker 客户端"
        return self._docker_client.start_container(container_id)
    
    def start_container_async(self, container_id: str, callback=None) -> None:
        """异步启动容器"""
        if not self._docker_client:
            if callback:
                callback((False, "未初始化 Docker 客户端"))
            return
        
        self._current_worker = DockerOperationWorker(
            self._docker_client, "start_container", container_id
        )
        if callback:
            self._current_worker.operation_completed.connect(callback)
        self._current_worker.start()
    
    def stop_container(self, container_id: str) -> tuple[bool, str]:
        """停止容器（同步版本）"""
        if not self._docker_client:
            return False, "未初始化 Docker 客户端"
        return self._docker_client.stop_container(container_id)
    
    def stop_container_async(self, container_id: str, callback=None) -> None:
        """异步停止容器"""
        self._execute_operation("stop_container", container_id, callback)
    
    def restart_container(self, container_id: str) -> tuple[bool, str]:
        """重启容器（同步版本）"""
        if not self._docker_client:
            return False, "未初始化 Docker 客户端"
        return self._docker_client.restart_container(container_id)
    
    def restart_container_async(self, container_id: str, callback=None) -> None:
        """异步重启容器"""
        self._execute_operation("restart_container", container_id, callback)
    
    def remove_container(self, container_id: str, force: bool = False) -> tuple[bool, str]:
        """删除容器（同步版本）"""
        if not self._docker_client:
            return False, "未初始化 Docker 客户端"
        return self._docker_client.remove_container(container_id, force=force)
    
    def remove_container_async(self, container_id: str, force: bool = False, callback=None) -> None:
        """异步删除容器"""
        self._execute_operation("remove_container", container_id, force=force, callback=callback)
    
    def get_container_logs(self, container_id: str, tail: int = 200) -> str:
        """获取容器日志（同步版本）"""
        if not self._docker_client:
            return ""
        return self._docker_client.get_container_logs(container_id, tail=tail)
    
    def get_container_logs_async(self, container_id: str, tail: int = 200, callback=None) -> None:
        """异步获取容器日志"""
        self._execute_operation("get_logs", container_id, tail=tail, callback=callback)
    
    def get_container_stats(self, container_id: str) -> dict:
        """获取容器资源统计（同步版本）"""
        if not self._docker_client:
            return {}
        return self._docker_client.get_container_stats(container_id)
    
    def get_container_stats_async(self, container_id: str, callback=None) -> None:
        """异步获取容器资源统计"""
        self._execute_operation("get_stats", container_id, callback=callback)
    
    def _execute_operation(self, operation: str, *args, callback=None, **kwargs):
        """执行操作的通用方法"""
        if not self._docker_client:
            if callback:
                callback((False, "未初始化 Docker 客户端"))
            return
        
        self._current_worker = DockerOperationWorker(
            self._docker_client, operation, *args, **kwargs
        )
        if callback:
            self._current_worker.operation_completed.connect(callback)
        self._current_worker.start()
    
    def get_client(self) -> Optional[DockerClient]:
        """获取底层 Docker 客户端（用于兼容现有代码）"""
        return self._docker_client
