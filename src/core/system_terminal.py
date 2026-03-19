"""
系统终端调用模块
调用 macOS 原生 Terminal 应用连接 SSH
"""
import subprocess
import os
from typing import Optional

from core.ssh_client import SSHConfig


class SystemTerminal:
    """系统终端调用器"""
    
    @staticmethod
    def open_terminal(ssh_config: SSHConfig, command: Optional[str] = None):
        """
        打开系统终端并连接到服务器
        
        Args:
            ssh_config: SSH 配置
            command: 可选的初始命令
        """
        # 构建 SSH 连接命令
        ssh_cmd = f"ssh {ssh_config.username}@{ssh_config.hostname} -p {ssh_config.port}"
        
        # 如果有密钥文件，添加到命令中
        if ssh_config.key_filename:
            ssh_cmd += f" -i {ssh_config.key_filename}"
        
        # 如果有要执行的命令
        if command:
            ssh_cmd += f" '{command}'"
        
        # macOS 使用 AppleScript 打开 Terminal 并执行命令
        script = f'''
        tell application "Terminal"
            activate
            do script "{ssh_cmd}"
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            print(f"[SystemTerminal] 已打开终端窗口：{ssh_cmd}")
        except subprocess.CalledProcessError as e:
            print(f"[SystemTerminal] 打开终端失败：{e}")
            raise RuntimeError(f"无法打开系统终端：{e}")
    
    @staticmethod
    def open_local_terminal():
        """打开本地终端"""
        script = '''
        tell application "Terminal"
            activate
            do script ""
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[SystemTerminal] 打开本地终端失败：{e}")
    
    @staticmethod
    def open_iterm2(ssh_config: SSHConfig, command: Optional[str] = None):
        """
        打开 iTerm2 终端并连接到服务器（如果安装了 iTerm2）
        
        Args:
            ssh_config: SSH 配置
            command: 可选的初始命令
        """
        ssh_cmd = f"ssh {ssh_config.username}@{ssh_config.hostname} -p {ssh_config.port}"
        
        if ssh_config.key_filename:
            ssh_cmd += f" -i {ssh_config.key_filename}"
        
        if command:
            ssh_cmd += f" '{command}'"
        
        # 检查是否安装了 iTerm2
        iterm2_path = "/Applications/iTerm.app"
        if not os.path.exists(iterm2_path):
            # 降级到普通 Terminal
            return SystemTerminal.open_terminal(ssh_config, command)
        
        script = f'''
        tell application "iTerm"
            activate
            create window with default profile
            tell current session of current window
                write text "{ssh_cmd}"
            end tell
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            print(f"[SystemTerminal] 已打开 iTerm2 窗口：{ssh_cmd}")
        except subprocess.CalledProcessError as e:
            print(f"[SystemTerminal] 打开 iTerm2 失败，降级到 Terminal: {e}")
            SystemTerminal.open_terminal(ssh_config, command)
