"""
系统信息解析工具模块
解析 Linux 系统命令输出，提取监控数据
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CPUInfo:
    """CPU 信息"""
    usage_percent: float  # 使用率百分比
    cores: int  # 核心数
    model: str  # 型号


@dataclass
class MemoryInfo:
    """内存信息"""
    total: int  # 总内存 (KB)
    used: int  # 已用内存 (KB)
    free: int  # 空闲内存 (KB)
    available: int  # 可用内存 (KB)
    usage_percent: float  # 使用率百分比


@dataclass
class DiskInfo:
    """磁盘信息"""
    mount_point: str  # 挂载点
    total: int  # 总空间 (KB)
    used: int  # 已用空间 (KB)
    free: int  # 剩余空间 (KB)
    usage_percent: float  # 使用率百分比


@dataclass
class NetworkInfo:
    """网络信息"""
    interface: str  # 网卡名称
    bytes_received: int  # 接收字节数
    bytes_sent: int  # 发送字节数
    packets_received: int  # 接收包数
    packets_sent: int  # 发送包数


@dataclass
class SystemLoad:
    """系统负载"""
    load_1min: float  # 1 分钟平均负载
    load_5min: float  # 5 分钟平均负载
    load_15min: float  # 15 分钟平均负载
    running_processes: int  # 运行中进程数
    total_processes: int  # 总进程数


class SystemParser:
    """系统信息解析器"""
    
    @staticmethod
    def parse_cpu_info(output: str) -> Optional[CPUInfo]:
        """
        解析 CPU 信息（来自 /proc/cpuinfo 或 top 命令）
        
        Args:
            output: 命令输出
            
        Returns:
            CPUInfo 对象或 None
        """
        if not output or not isinstance(output, str):
            return None
        
        output = output.strip()
        if not output:
            return None
        
        lines = output.split('\n')
        cores = 0
        model = ""
        
        for line in lines:
            if 'processor' in line.lower():
                cores += 1
            elif 'model name' in line.lower() and not model:
                match = re.search(r':\s*(.+)', line)
                if match:
                    model = match.group(1).strip()
        
        # 如果无法解析核心数，至少返回 1
        if cores == 0:
            cores = 1
        
        return CPUInfo(
            usage_percent=0.0,  # 需要单独计算
            cores=cores,
            model=model or "Unknown"
        )
    
    @staticmethod
    def parse_top_cpu(output: str) -> float:
        """
        从 top 命令解析 CPU 使用率
        
        Args:
            output: top 命令输出
            
        Returns:
            CPU 使用率百分比
        """
        if not output or not isinstance(output, str):
            return 0.0
        
        output = output.strip()
        if not output:
            return 0.0
        
        # 匹配类似 "Cpu(s):  2.3 us,  1.0 sy,  0.0 ni, 96.7 id, ..."
        match = re.search(r'Cpu\(s\):\s*([\d.]+)\s*us', output)
        if match:
            user = float(match.group(1))
            # 也获取 system
            sys_match = re.search(r'([\d.]+)\s*sy', output)
            system = float(sys_match.group(1)) if sys_match else 0.0
            return user + system
        
        # 尝试匹配简化格式
        match = re.search(r'(\d+\.?\d*)\s*(?:id|wa)', output)
        if match:
            idle = float(match.group(1))
            return 100.0 - idle
        
        return 0.0
    
    @staticmethod
    def parse_memory_info(output: str) -> Optional[MemoryInfo]:
        """
        解析内存信息（来自 free 命令）
        
        Args:
            output: free 命令输出
            
        Returns:
            MemoryInfo 对象或 None
        """
        if not output or not isinstance(output, str):
            return None
        
        output = output.strip()
        if not output:
            return None
        
        lines = output.split('\n')
        if len(lines) < 2:
            return None
        
        # 查找以 Mem: 开头的行
        for line in lines:
            if line.startswith('Mem:'):
                parts = line.split()
                if len(parts) >= 7:
                    try:
                        total = int(parts[1])
                        used = int(parts[2])
                        free = int(parts[3])
                        available = int(parts[6]) if len(parts) > 6 else free
                        
                        usage_percent = (used / total * 100) if total > 0 else 0.0
                        
                        return MemoryInfo(
                            total=total,
                            used=used,
                            free=free,
                            available=available,
                            usage_percent=usage_percent
                        )
                    except (ValueError, IndexError):
                        pass
        
        return None
    
    @staticmethod
    def parse_disk_info(output: str) -> List[DiskInfo]:
        """
        解析磁盘信息（来自 df 命令）
        
        Args:
            output: df 命令输出
            
        Returns:
            DiskInfo 对象列表
        """
        if not output or not isinstance(output, str):
            return []
        
        output = output.strip()
        if not output:
            return []
        
        disks = []
        lines = output.split('\n')
        
        # 跳过标题行
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 6:
                try:
                    # df -k 输出格式：Filesystem 1K-blocks Used Available Use% Mounted
                    filesystem = parts[0]
                    # 跳过虚拟文件系统
                    if filesystem.startswith(('tmpfs', 'devtmpfs', 'none')):
                        continue
                    
                    total = int(parts[1])
                    used = int(parts[2])
                    free = int(parts[3])
                    usage_str = parts[4].rstrip('%')
                    usage_percent = float(usage_str)
                    mount_point = parts[5]
                    
                    disks.append(DiskInfo(
                        mount_point=mount_point,
                        total=total,
                        used=used,
                        free=free,
                        usage_percent=usage_percent
                    ))
                except (ValueError, IndexError):
                    continue
        
        return disks
    
    @staticmethod
    def parse_network_info(output: str) -> List[NetworkInfo]:
        """
        解析网络信息（来自 /proc/net/dev 或 netstat）
        
        Args:
            output: /proc/net/dev 内容
            
        Returns:
            NetworkInfo 对象列表
        """
        if not output or not isinstance(output, str):
            return []
        
        output = output.strip()
        if not output:
            return []
        
        networks = []
        lines = output.split('\n')
        
        # 跳过标题行（至少需要 2 行）
        if len(lines) < 3:
            return networks
        
        for line in lines[2:]:
            if ':' not in line:
                continue
            
            parts = line.split(':')
            if len(parts) != 2:
                continue
            
            interface = parts[0].strip()
            # 跳过 loopback 和虚拟接口
            if interface in ('lo', 'docker0') or interface.startswith('veth'):
                continue
            
            stats = parts[1].split()
            if len(stats) >= 10:
                try:
                    networks.append(NetworkInfo(
                        interface=interface,
                        bytes_received=int(stats[0]),
                        packets_received=int(stats[1]),
                        bytes_sent=int(stats[8]),
                        packets_sent=int(stats[9])
                    ))
                except (ValueError, IndexError):
                    continue
        
        return networks
    
    @staticmethod
    def parse_system_load(output: str) -> Optional[SystemLoad]:
        """
        解析系统负载（来自 uptime 或 /proc/loadavg）
        
        Args:
            output: uptime 命令输出
            
        Returns:
            SystemLoad 对象或 None
        """
        if not output or not isinstance(output, str):
            return None
        
        output = output.strip()
        if not output:
            return None
        
        # 匹配类似："load average: 0.15, 0.10, 0.05"
        match = re.search(r'load average:\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)', output)
        if match:
            # 尝试解析进程数 "0/123"
            proc_match = re.search(r'(\d+)/(\d+)', output)
            if proc_match:
                running = int(proc_match.group(1))
                total = int(proc_match.group(2))
            else:
                running = 0
                total = 0
            
            return SystemLoad(
                load_1min=float(match.group(1)),
                load_5min=float(match.group(2)),
                load_15min=float(match.group(3)),
                running_processes=running,
                total_processes=total
            )
        
        return None
    
    @staticmethod
    def format_size(size_kb: int) -> str:
        """
        格式化大小显示
        
        Args:
            size_kb: 大小（KB）
            
        Returns:
            格式化后的字符串（如 "1.5 GB"）
        """
        if size_kb < 1024:
            return f"{size_kb} KB"
        elif size_kb < 1024 * 1024:
            return f"{size_kb / 1024:.1f} MB"
        elif size_kb < 1024 * 1024 * 1024:
            return f"{size_kb / (1024 * 1024):.1f} GB"
        else:
            return f"{size_kb / (1024 * 1024 * 1024):.2f} TB"
