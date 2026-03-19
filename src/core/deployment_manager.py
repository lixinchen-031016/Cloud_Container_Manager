"""
Docker 容器部署模块
支持 docker-compose 和单个容器部署
"""
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from core.docker_client import DockerClient


@dataclass
class PortMapping:
    """端口映射配置"""
    host_port: int
    container_port: int
    protocol: str = "tcp"
    
    def to_docker_string(self) -> str:
        """转换为 Docker 格式"""
        return f"{self.host_port}:{self.container_port}/{self.protocol}"


@dataclass 
class VolumeMapping:
    """卷映射配置"""
    host_path: str
    container_path: str
    mode: str = "ro"  # ro 或 rw
    
    def to_docker_string(self) -> str:
        """转换为 Docker 格式"""
        return f"{self.host_path}:{self.container_path}:{self.mode}"


@dataclass
class ContainerDeployment:
    """容器部署配置"""
    name: str
    image: str
    ports: List[PortMapping]
    volumes: List[VolumeMapping]
    environment: Dict[str, str]
    command: Optional[str] = None
    restart_policy: str = "unless-stopped"  # always, unless-stopped, on-failure, no
    network: Optional[str] = None
    
    def to_docker_run_args(self) -> Dict:
        """转换为 docker run 参数字典"""
        args = {
            'image': self.image,
            'detach': True,
            'name': self.name,
            'restart_policy': {'Name': self.restart_policy},
        }
        
        # 端口映射
        if self.ports:
            port_bindings = {}
            for port in self.ports:
                key = f"{port.container_port}/{port.protocol}"
                port_bindings[key] = [{'HostPort': str(port.host_port)}]
            args['ports'] = port_bindings
        
        # 卷映射
        if self.volumes:
            args['volumes'] = {
                f"{vol.host_path}:{vol.container_path}": {'bind': vol.container_path, 'mode': vol.mode}
                for vol in self.volumes
            }
        
        # 环境变量
        if self.environment:
            args['environment'] = [f"{k}={v}" for k, v in self.environment.items()]
        
        # 命令
        if self.command:
            args['command'] = self.command
        
        # 网络
        if self.network:
            args['network'] = self.network
        
        return args


class DeploymentManager:
    """部署管理器"""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
    
    def deploy_container(self, deployment: ContainerDeployment) -> Tuple[bool, str]:
        """
        部署容器
        
        Args:
            deployment: 容器部署配置
            
        Returns:
            (成功标志，消息)
        """
        try:
            args = deployment.to_docker_run_args()
            
            # 运行容器
            container = self.docker_client.ssh_client._client  # 访问底层 paramiko client
            
            # 构建 docker run 命令
            cmd_parts = ["docker run -d"]
            
            # 名称
            cmd_parts.append(f"--name {deployment.name}")
            
            # 重启策略
            cmd_parts.append(f"--restart {deployment.restart_policy}")
            
            # 端口
            for port in deployment.ports:
                cmd_parts.append(f"-p {port.host_port}:{port.container_port}/{port.protocol}")
            
            # 卷
            for vol in deployment.volumes:
                cmd_parts.append(f"-v {vol.host_path}:{vol.container_path}:{vol.mode}")
            
            # 环境变量
            for key, value in deployment.environment.items():
                cmd_parts.append(f"-e {key}={value}")
            
            # 网络
            if deployment.network:
                cmd_parts.append(f"--network {deployment.network}")
            
            # 镜像和命令
            cmd_parts.append(deployment.image)
            if deployment.command:
                cmd_parts.append(deployment.command)
            
            # 执行命令
            cmd = " ".join(cmd_parts)
            exit_code, output, error = self.docker_client.ssh_client.exec_command(cmd, timeout=60)
            
            if exit_code == 0:
                return True, f"容器 {deployment.name} 部署成功"
            else:
                return False, f"部署失败：{error}"
                
        except Exception as e:
            return False, f"部署异常：{str(e)}"
    
    def remove_container(self, container_id: str, force: bool = True) -> Tuple[bool, str]:
        """删除容器"""
        return self.docker_client.remove_container(container_id, force=force)
    
    def generate_compose_file(self, deployments: List[ContainerDeployment]) -> str:
        """
        生成 docker-compose.yml 内容
        
        Args:
            deployments: 容器部署配置列表
            
        Returns:
            docker-compose.yml 文件内容
        """
        compose = {
            'version': '3.8',
            'services': {}
        }
        
        for deployment in deployments:
            service = {
                'image': deployment.image,
                'container_name': deployment.name,
                'restart': deployment.restart_policy,
            }
            
            # 端口
            if deployment.ports:
                service['ports'] = [port.to_docker_string() for port in deployment.ports]
            
            # 卷
            if deployment.volumes:
                service['volumes'] = [vol.to_docker_string() for vol in deployment.volumes]
            
            # 环境变量
            if deployment.environment:
                service['environment'] = deployment.environment
            
            # 命令
            if deployment.command:
                service['command'] = deployment.command
            
            # 网络
            if deployment.network:
                service['networks'] = [deployment.network]
            
            compose['services'][deployment.name] = service
        
        # 添加网络定义
        networks = set()
        for deployment in deployments:
            if deployment.network:
                networks.add(deployment.network)
        
        if networks:
            compose['networks'] = {net: {'driver': 'bridge'} for net in networks}
        
        import yaml
        return yaml.dump(compose, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def deploy_compose(self, compose_content: str, project_name: str) -> Tuple[bool, str]:
        """
        使用 docker-compose 部署
        
        Args:
            compose_content: docker-compose.yml 内容
            project_name: 项目名称
            
        Returns:
            (成功标志，消息)
        """
        try:
            ssh_client = self.docker_client.ssh_client
            
            # 在远程服务器创建临时文件
            import tempfile
            import os
            
            # 写入 compose 文件到远程服务器
            remote_path = f"/tmp/{project_name}_docker-compose.yml"
            
            # 使用 SFTP 上传文件
            sftp = ssh_client._client.open_sftp()
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(compose_content)
                temp_path = f.name
            
            try:
                sftp.put(temp_path, remote_path)
                sftp.close()
                
                # 执行 docker-compose up
                cmd = f"cd /tmp && docker-compose -p {project_name} -f {remote_path} up -d"
                exit_code, output, error = ssh_client.exec_command(cmd, timeout=120)
                
                # 清理临时文件
                ssh_client.exec_command(f"rm {remote_path}")
                
                if exit_code == 0:
                    return True, f"项目 {project_name} 部署成功"
                else:
                    return False, f"部署失败：{error}"
                    
            finally:
                os.unlink(temp_path)
                
        except Exception as e:
            return False, f"部署异常：{str(e)}"
