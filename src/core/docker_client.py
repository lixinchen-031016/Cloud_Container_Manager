"""
Docker 客户端封装模块
通过 SSH 隧道管理远程 Docker 容器
"""
import json
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from .ssh_client import SSHClient


@dataclass
class ContainerInfo:
    """容器信息"""
    id: str
    name: str
    image: str
    status: str
    state: str
    ports: str
    created: str


class DockerClient:
    """Docker 客户端封装类（通过 SSH）"""
    
    def __init__(self, ssh_client: SSHClient):
        """
        初始化 Docker 客户端
        
        Args:
            ssh_client: 已连接的 SSH 客户端实例
        """
        self.ssh_client = ssh_client
    
    def _run_docker_command(self, command: str) -> tuple:
        """执行 Docker 命令"""
        full_command = f"docker {command}"
        return self.ssh_client.exec_command(full_command)
    
    def list_containers(self, all: bool = False) -> List[ContainerInfo]:
        """
        列出容器
        
        Args:
            all: 是否包含所有容器（包括已停止的）
            
        Returns:
            容器信息列表
        """
        flag = "-a" if all else ""
        exit_code, output, error = self._run_docker_command(
            f"ps {flag} --format '{{{{json .}}}}'"
        )
        
        if exit_code != 0:
            raise RuntimeError(f"Docker 命令失败：{error}")
        
        containers = []
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                container = ContainerInfo(
                    id=data.get('ID', '')[:12],
                    name=data.get('Names', ''),
                    image=data.get('Image', ''),
                    status=data.get('Status', ''),
                    state=data.get('State', ''),
                    ports=data.get('Ports', ''),
                    created=data.get('CreatedAt', '')
                )
                containers.append(container)
            except json.JSONDecodeError:
                continue
        
        return containers
    
    def get_container(self, container_id: str) -> Optional[ContainerInfo]:
        """获取单个容器详情"""
        exit_code, output, error = self._run_docker_command(
            f"inspect {container_id} --format '{{{{json .}}}}'"
        )
        
        if exit_code != 0:
            return None
        
        try:
            data = json.loads(output.strip())
            return ContainerInfo(
                id=data.get('Id', '')[:12],
                name=data.get('Name', '').lstrip('/'),
                image=data.get('Config', {}).get('Image', ''),
                status=data.get('State', {}).get('Status', ''),
                state=data.get('State', {}).get('Status', ''),
                ports=self._format_ports(data.get('NetworkSettings', {}).get('Ports', {})),
                created=data.get('Created', '')
            )
        except (json.JSONDecodeError, KeyError):
            return None
    
    def _format_ports(self, ports: dict) -> str:
        """格式化端口映射"""
        if not ports:
            return ""
        
        port_list = []
        for host_port, bindings in ports.items():
            if bindings:
                for binding in bindings:
                    port_list.append(f"{binding['HostIp']}:{binding['HostPort']}->{host_port}")
        
        return ", ".join(port_list)
    
    def start_container(self, container_id: str) -> tuple:
        """启动容器"""
        exit_code, output, error = self._run_docker_command(f"start {container_id}")
        return exit_code == 0, error if exit_code != 0 else "启动成功"
    
    def stop_container(self, container_id: str, timeout: int = 10) -> tuple:
        """停止容器"""
        exit_code, output, error = self._run_docker_command(
            f"stop -t {timeout} {container_id}"
        )
        return exit_code == 0, error if exit_code != 0 else "停止成功"
    
    def restart_container(self, container_id: str) -> tuple:
        """重启容器"""
        exit_code, output, error = self._run_docker_command(f"restart {container_id}")
        return exit_code == 0, error if exit_code != 0 else "重启成功"
    
    def remove_container(self, container_id: str, force: bool = False) -> tuple:
        """删除容器"""
        flag = "-f" if force else ""
        exit_code, output, error = self._run_docker_command(f"rm {flag} {container_id}")
        return exit_code == 0, error if exit_code != 0 else "删除成功"
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """
        获取容器日志
        
        Args:
            container_id: 容器 ID
            tail: 显示最后多少行
            
        Returns:
            日志内容
        """
        exit_code, output, error = self._run_docker_command(
            f"logs --tail {tail} {container_id} 2>&1"
        )
        
        if exit_code != 0:
            raise RuntimeError(f"获取日志失败：{error}")
        
        return output
    
    def stream_container_logs(self, container_id: str, callback: Callable[[str], None]):
        """
        流式获取容器日志（实时）
        
        Args:
            container_id: 容器 ID
            callback: 回调函数，接收每一行日志
        """
        # 使用 tail -f 方式持续输出日志
        def log_callback(line):
            if callback:
                callback(line)
        
        self.ssh_client.exec_command_streaming(
            f"docker logs -f {container_id}",
            callback=log_callback
        )
    
    def get_container_stats(self, container_id: str) -> Optional[Dict]:
        """
        获取容器资源统计
        
        Args:
            container_id: 容器 ID
            
        Returns:
            资源统计信息字典
        """
        # 获取单条统计信息
        exit_code, output, error = self._run_docker_command(
            f"stats --no-stream --format '{{{{json .}}}}' {container_id}"
        )
        
        if exit_code != 0:
            return None
        
        try:
            return json.loads(output.strip())
        except json.JSONDecodeError:
            return None
    
    def execute_command(self, container_id: str, command: str) -> tuple:
        """
        在容器内执行命令
        
        Args:
            container_id: 容器 ID
            command: 要执行的命令
            
        Returns:
            (成功标志，输出或错误信息)
        """
        exit_code, output, error = self._run_docker_command(
            f"exec {container_id} {command}"
        )
        return exit_code == 0, output if exit_code == 0 else error
