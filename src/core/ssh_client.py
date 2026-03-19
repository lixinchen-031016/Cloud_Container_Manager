"""
SSH 客户端封装模块
提供 SSH 连接、命令执行等功能
"""
import paramiko
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class SSHConfig:
    """SSH 连接配置"""
    hostname: str
    port: int = 22
    username: str = ""
    password: Optional[str] = None
    key_filename: Optional[str] = None
    passphrase: Optional[str] = None
    
    def __post_init__(self):
        if not self.username:
            raise ValueError("用户名不能为空")
        if not self.password and not self.key_filename:
            raise ValueError("密码或密钥文件必须提供一个")


class SSHClient:
    """SSH 客户端封装类"""
    
    def __init__(self):
        self._client: Optional[paramiko.SSHClient] = None
        self._config: Optional[SSHConfig] = None
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self._client is not None
    
    @property
    def config(self) -> Optional[SSHConfig]:
        """获取当前配置"""
        return self._config
    
    def connect(self, config: SSHConfig, timeout: int = 10, accept_unknown_host: bool = True) -> Tuple[bool, str]:
        """
        连接到 SSH 服务器
        
        Args:
            config: SSH 连接配置
            timeout: 连接超时时间（秒）
            accept_unknown_host: 是否自动接受未知主机密钥（默认 True）
            
        Returns:
            (成功标志，错误信息)
        """
        try:
            self._client = paramiko.SSHClient()
            
            # 设置主机密钥策略
            if accept_unknown_host:
                # 自动添加未知主机密钥（开发/测试环境）
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                # 使用系统 known_hosts 文件（生产环境更安全）
                self._client.load_system_host_keys()
                self._client.set_missing_host_key_policy(paramiko.RejectPolicy())
            
            self._config = config
            
            # 准备连接参数
            connect_kwargs = {
                'hostname': config.hostname,
                'port': config.port,
                'username': config.username,
                'timeout': timeout,
                'allow_agent': False,
                'look_for_keys': False,
            }
            
            # 添加认证方式
            if config.password:
                connect_kwargs['password'] = config.password
            elif config.key_filename:
                connect_kwargs['key_filename'] = config.key_filename
                if config.passphrase:
                    connect_kwargs['passphrase'] = config.passphrase
            
            # 执行连接
            self._client.connect(**connect_kwargs)
            self._connected = True
            return True, "连接成功"
            
        except paramiko.AuthenticationException:
            return False, "认证失败：用户名或密码错误"
        except paramiko.SSHException as e:
            if 'host key' in str(e).lower():
                return False, f"主机密钥验证失败：{str(e)}\n\n解决方法：运行 'ssh-keygen -R {config.hostname}' 清除旧密钥"
            return False, f"SSH 错误：{str(e)}"
        except Exception as e:
            return False, f"连接失败：{str(e)}"
    
    def disconnect(self):
        """断开 SSH 连接"""
        if self._client:
            try:
                self._client.close()
            except:
                pass
            finally:
                self._client = None
                self._connected = False
                self._config = None
    
    def exec_command(self, command: str, timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
            timeout: 命令执行超时时间（秒）
            
        Returns:
            (返回码，标准输出，标准错误)
        """
        if not self.is_connected:
            error_msg = "未连接到 SSH 服务器"
            print(f"[SSH ERROR] {error_msg}")
            raise RuntimeError(error_msg)
        
        try:
            print(f"[SSH] 执行命令：{command[:50]}...")
            stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout)
            
            # 等待 channel ready
            channel = stdout.channel
            print(f"[SSH] Channel exit_status_ready: {channel.exit_status_ready()}")
            print(f"[SSH] Channel recv_ready: {channel.recv_ready()}")
            print(f"[SSH] Channel stderr_recv_ready: {channel.recv_stderr_ready()}")
            
            # 设置超时
            if timeout:
                channel.settimeout(timeout)
            
            # 读取输出
            output_chunks = []
            error_chunks = []
            read_attempts = 0
            max_attempts = 50  # 最多尝试 50 次
            
            while not channel.exit_status_ready() and read_attempts < max_attempts:
                if channel.recv_ready():
                    data = channel.recv(4096)
                    print(f"[SSH] 接收到数据：{len(data)} bytes")
                    if data:
                        output_chunks.append(data.decode('utf-8', errors='replace'))
                
                if channel.recv_stderr_ready():
                    data = channel.recv_stderr(4096)
                    if data:
                        error_chunks.append(data.decode('utf-8', errors='replace'))
                
                read_attempts += 1
                import time
                time.sleep(0.1)  # 等待 100ms
            
            # 获取退出码
            exit_code = channel.recv_exit_status()
            print(f"[SSH] 退出码：{exit_code}")
            
            # 读取剩余输出
            while channel.recv_ready():
                data = channel.recv(4096)
                if not data:
                    break
                output_chunks.append(data.decode('utf-8', errors='replace'))
            
            while channel.recv_stderr_ready():
                data = channel.recv_stderr(4096)
                if not data:
                    break
                error_chunks.append(data.decode('utf-8', errors='replace'))
            
            output = ''.join(output_chunks)
            error = ''.join(error_chunks)
            
            print(f"[SSH] 最终输出长度：{len(output)}, 错误长度：{len(error)}")
            
            if exit_code != 0 and error:
                print(f"[SSH WARNING] 命令 '{command}' 执行失败，退出码：{exit_code}, 错误：{error[:200]}")
            
            return exit_code, output, error
            
        except Exception as e:
            print(f"[SSH ERROR] 执行命令 '{command}' 失败：{e}")
            import traceback
            traceback.print_exc()
            raise
    
    def exec_command_streaming(self, command: str, callback=None):
        """
        执行命令并流式输出（适用于日志查看）
        
        Args:
            command: 要执行的命令
            callback: 回调函数，接收输出行
        """
        if not self.is_connected:
            raise RuntimeError("未连接到 SSH 服务器")
        
        stdin, stdout, stderr = self._client.exec_command(command)
        
        # 读取标准输出
        for line in iter(stdout.readline, ''):
            if callback:
                callback(line.rstrip('\n'))
        
        # 读取标准错误
        for line in iter(stderr.readline, ''):
            if callback:
                stripped_line = line.rstrip('\n')
                callback(f"[ERROR] {stripped_line}")
        
        return stdout.channel.recv_exit_status()
    
    def get_file(self, remote_path: str, local_path: str):
        """下载远程文件"""
        if not self.is_connected:
            raise RuntimeError("未连接到 SSH 服务器")
        
        sftp = self._client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()
    
    def put_file(self, local_path: str, remote_path: str):
        """上传本地文件"""
        if not self.is_connected:
            raise RuntimeError("未连接到 SSH 服务器")
        
        sftp = self._client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()
