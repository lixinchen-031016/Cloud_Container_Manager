# Cloud Container Manager

一个 macOS 原生的 Python GUI 应用程序，用于连接云端服务器并管理 Docker 容器。

## 功能特性

- **SSH 连接管理**: 支持密码和密钥认证
- **服务器监控**: 实时查看 CPU、内存、磁盘、网络使用情况
- **容器管理**: 查看容器列表、控制启停、查看日志
- **macOS 原生界面**: 使用 PyQt6 构建现代化界面

## 安装依赖

### 使用虚拟环境（推荐）

```bash
# 创建并激活 Python 3.11 虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 不使用虚拟环境

```bash
pip install -r requirements.txt
```

## 运行应用

### 使用虚拟环境

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行应用
python src/main.py
```

### 不使用虚拟环境

```bash
python src/main.py
```

## 打包为 .app

```bash
chmod +x build_app.sh
./build_app.sh
```

生成的应用将在 `dist/CloudManager.app` 目录中。

## 技术栈

- **GUI 框架**: PyQt6
- **SSH 连接**: paramiko
- **Docker 管理**: docker-py
- **打包工具**: PyInstaller

## 系统要求

- macOS 10.15+
- Python 3.8+
- Docker (远程服务器)
