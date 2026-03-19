"""
SSH 连接调试脚本
用于测试 SSH 连接和命令执行
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from core.ssh_client import SSHClient, SSHConfig


def test_ssh_connection():
    """测试 SSH 连接和命令执行"""
    print("=" * 60)
    print("SSH 连接调试工具")
    print("=" * 60)
    
    # 获取服务器信息
    hostname = input("\n请输入服务器主机名或 IP: ").strip()
    port = input("请输入 SSH 端口 (默认 22): ").strip() or "22"
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    
    # 创建配置
    config = SSHConfig(
        hostname=hostname,
        port=int(port),
        username=username,
        password=password
    )
    
    # 创建客户端并连接
    client = SSHClient()
    print(f"\n正在连接到 {hostname}:{port}...")
    
    success, message = client.connect(config)
    
    if not success:
        print(f"❌ 连接失败：{message}")
        return
    
    print(f"✅ 连接成功！")
    print(f"SSH 客户端对象 ID: {id(client)}")
    print(f"连接状态：{client.is_connected}")
    
    # 测试命令执行
    print("\n" + "=" * 60)
    print("测试命令执行")
    print("=" * 60)
    
    commands = [
        "cat /proc/cpuinfo",
        "top -bn1 | head -n 5",
        "free -k",
        "df -k",
        "cat /proc/net/dev",
        "uptime"
    ]
    
    for cmd in commands:
        print(f"\n执行命令：{cmd}")
        try:
            exit_code, output, error = client.exec_command(cmd, timeout=5)
            print(f"退出码：{exit_code}")
            print(f"输出长度：{len(output)}")
            print(f"错误：{error if error else '无'}")
            
            if output:
                print(f"输出预览（前 100 字符）：{output[:100]}...")
        except Exception as e:
            print(f"❌ 执行失败：{e}")
    
    # 断开连接
    print("\n" + "=" * 60)
    print("断开连接")
    print("=" * 60)
    client.disconnect()
    print(f"连接已断开")
    print(f"SSH 客户端对象：{client._client}")
    print(f"连接状态：{client.is_connected}")


if __name__ == "__main__":
    try:
        test_ssh_connection()
    except KeyboardInterrupt:
        print("\n\n程序中断")
        sys.exit(0)
