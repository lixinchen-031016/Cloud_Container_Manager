"""
测试监控数据解析
验证从 SSH 命令输出到 UI 显示的完整流程
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from utils.system_parser import SystemParser


def test_parsers():
    """测试所有解析器"""
    print("=" * 60)
    print("测试系统信息解析器")
    print("=" * 60)
    
    # 模拟真实的命令输出
    cpu_output = """processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 85
model name	: Intel(R) Xeon(R) Platinum 8269CY CPU @ 2.50GHz
stepping	: 7
microcode	: 0x5003604
cpu MHz		: 2500.000
cache size	: 36608 KB
physical id	: 0
siblings	: 4
core id		: 0
cpu cores	: 4
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 22
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl xtopology tsc_reliable nonstop_tsc cpuid pni pclmulqdq vmx ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid avx512f avx512dq rdseed adx smap avx512ifma clflushopt clwb avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves avx512vbmi umip avx512vbmi2 gfni vaes vpclmulqdq avx512vnni avx512bitalg avx512vpopcntdq rdpid arch_capabilities
bugs		: spectre_v1 spectre_v2 spec_store_bypass swapgs itlb_multihit mmio_stale_data eibrs_unaffected_lbrr gds bhi
bogomips	: 5000.00
clflush_size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 1
vendor_id	: GenuineIntel
cpu family	: 6
model		: 85
model name	: Intel(R) Xeon(R) Platinum 8269CY CPU @ 2.50GHz
stepping	: 7
microcode	: 0x5003604
cpu MHz		: 2500.000
cache size	: 36608 KB
physical id	: 0
siblings	: 4
core id		: 1
cpu cores	: 4
apicid		: 2
initial apicid	: 2
fpu		: yes
fpu_exception	: yes
cpuid level	: 22
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl xtopology tsc_reliable nonstop_tsc cpuid pni pclmulqdq vmx ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid avx512f avx512dq rdseed adx smap avx512ifma clflushopt clwb avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves avx512vbmi umip avx512vbmi2 gfni vaes vpclmulqdq avx512vnni avx512bitalg avx512vpopcntdq rdpid arch_capabilities
bugs		: spectre_v1 spectre_v2 spec_store_bypass swapgs itlb_multihit mmio_stale_data eibrs_unaffected_lbrr gds bhi
bogomips	: 5000.00
clflush_size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:
"""
    
    top_output = """top - 21:33:03 up 50 days,  1:14,  1 user,  load average: 0.00, 0.05, 0.01
Tasks: 128 total,   1 running, 127 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.3 us,  0.3 sy,  0.0 ni, 99.4 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st 
MiB Mem :  32000.0 total,  15000.0 free,   8000.0 used,   9000.0 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.  24000.0 avail Mem 
"""
    
    mem_output = """              total        used        free      shared  buff/cache   available
Mem:        32768000     8000000    15000000      100000     9768000    24000000
Swap:              0           0           0
"""
    
    disk_output = """Filesystem     1K-blocks     Used Available Use% Mounted on
tmpfs             1651720     1264    1650456   1% /run
/dev/vda1      103081248  45678912  57402336  45% /
"""
    
    net_output = """Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo:  1000000     100    0    0    0     0          0         0  1000000     100    0    0    0     0       0          0
  eth0: 5000000000 5000000    0    0    0     0          0         0 3000000000 3000000    0    0    0     0       0          0
docker0:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
"""
    
    uptime_output = """ 21:33:04 up 50 days,  1:14,  1 user,  load average: 0.00, 0.05, 0.01
"""
    
    # 测试 CPU 解析
    print("\n1. 测试 CPU 解析")
    cpu_info = SystemParser.parse_cpu_info(cpu_output)
    if cpu_info:
        print(f"✓ CPU 核心数：{cpu_info.cores}")
        print(f"✓ CPU 型号：{cpu_info.model}")
        
        cpu_usage = SystemParser.parse_top_cpu(top_output)
        print(f"✓ CPU 使用率：{cpu_usage:.1f}%")
    else:
        print("✗ CPU 解析失败")
    
    # 测试内存解析
    print("\n2. 测试内存解析")
    mem_info = SystemParser.parse_memory_info(mem_output)
    if mem_info:
        print(f"✓ 总内存：{SystemParser.format_size(mem_info.total)}")
        print(f"✓ 已用内存：{SystemParser.format_size(mem_info.used)}")
        print(f"✓ 可用内存：{SystemParser.format_size(mem_info.available)}")
        print(f"✓ 使用率：{mem_info.usage_percent:.1f}%")
    else:
        print("✗ 内存解析失败")
    
    # 测试磁盘解析
    print("\n3. 测试磁盘解析")
    disks = SystemParser.parse_disk_info(disk_output)
    if disks:
        for disk in disks:
            print(f"✓ {disk.mount_point}: {disk.usage_percent}% ({SystemParser.format_size(disk.used)} / {SystemParser.format_size(disk.total)})")
    else:
        print("✗ 磁盘解析失败")
    
    # 测试网络解析
    print("\n4. 测试网络解析")
    networks = SystemParser.parse_network_info(net_output)
    if networks:
        for net in networks:
            rx_gb = net.bytes_received / (1024**3)
            tx_gb = net.bytes_sent / (1024**3)
            print(f"✓ {net.interface}: 接收 {rx_gb:.2f} GB, 发送 {tx_gb:.2f} GB")
    else:
        print("✗ 网络解析失败")
    
    # 测试系统负载解析
    print("\n5. 测试系统负载解析")
    load = SystemParser.parse_system_load(uptime_output)
    if load:
        print(f"✓ 1 分钟负载：{load.load_1min:.2f}")
        print(f"✓ 5 分钟负载：{load.load_5min:.2f}")
        print(f"✓ 15 分钟负载：{load.load_15min:.2f}")
        print(f"✓ 进程数：{load.running_processes}/{load.total_processes}")
    else:
        print("✗ 系统负载解析失败")
    
    print("\n" + "=" * 60)
    print("所有解析器测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_parsers()
