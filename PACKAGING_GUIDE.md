# CloudManager 打包与分发指南

## 📦 快速开始

### 当前机器架构打包（推荐用于开发测试）

```bash
cd /Users/lixinchen/codeProject
./build_for_current_arch.sh
```

这将针对当前机器（ARM64 - Apple Silicon）优化构建。

**输出位置**: `dist/CloudManager.app`

## 🏗️ 打包脚本说明

### 1. `build_for_current_arch.sh` - 单架构打包（推荐使用）
- **用途**: 为当前机器架构优化构建
- **优点**: 快速、简单、文件小（~39MB）
- **缺点**: 只支持一种架构
- **适用场景**: 
  - 开发测试
  - 内部使用（已知机器架构）

### 2. `build_universal.sh` - 双架构打包
- **用途**: 创建同时支持 ARM64 和 x86_64 的通用应用
- **要求**: 需要 Rosetta 2 安装
- **注意**: 由于 Python 包限制，建议在两种架构的 Mac 上分别构建后合并

### 3. `build_app_final.sh` - 标准打包
- **用途**: 使用优化配置打包
- **特点**: 包含更多 hiddenimports，适合复杂依赖

## 📋 构建步骤

### 方法 A: 单架构构建（快速）

```bash
# 1. 确保虚拟环境已激活
source venv/bin/activate

# 2. 运行打包脚本
./build_for_current_arch.sh

# 3. 验证结果
lipo -info dist/CloudManager.app/Contents/MacOS/CloudManager
# 输出：Non-fat file: ... is architecture: arm64

# 4. 测试运行
open dist/CloudManager.app
```

### 方法 B: 双架构构建（兼容所有 Mac）

#### 选项 1: 在两台不同架构的 Mac 上构建

**在 Apple Silicon Mac (M1/M2/M3) 上:**
```bash
./build_for_current_arch.sh
cp -r dist/CloudManager.app dist/CloudManager_ARM64.app
```

**在 Intel Mac 上:**
```bash
./build_for_current_arch.sh
cp -r dist/CloudManager.app dist/CloudManager_x86_64.app
```

**合并两个架构:**
```bash
mkdir -p Universal.app/Contents/MacOS
mkdir -p Universal.app/Contents/Resources

# 提取可执行文件
cp CloudManager_ARM64.app/Contents/MacOS/CloudManager ./temp_arm64
cp CloudManager_x86_64.app/Contents/MacOS/CloudManager ./temp_x86_64

# 合并
lipo -create temp_arm64 temp_x86_64 -output Universal.app/Contents/MacOS/CloudManager
chmod +x Universal.app/Contents/MacOS/CloudManager

# 复制资源
cp -r CloudManager_ARM64.app/Contents/Resources/* Universal.app/Contents/Resources/
cp CloudManager_ARM64.app/Contents/Info.plist Universal.app/Contents/

# 验证
lipo -info Universal.app/Contents/MacOS/CloudManager
# 输出：Architectures in the fat file: arm64 x86_64
```

#### 选项 2: 使用 GitHub Actions 自动构建

参考 `UNIVERSAL_BUILD_GUIDE.md` 中的 GitHub Actions 配置。

## ✅ 验证构建结果

### 1. 检查架构
```bash
lipo -info dist/CloudManager.app/Contents/MacOS/CloudManager
```

### 2. 检查文件大小
```bash
du -sh dist/CloudManager.app
# 单架构：~39MB
# 双架构：~80-90MB
```

### 3. 测试运行
```bash
# 图形界面
open dist/CloudManager.app

# 命令行（查看错误）
./dist/CloudManager.app/Contents/MacOS/CloudManager
```

### 4. 功能测试
- ✓ 连接 SSH 服务器
- ✓ 查看服务器监控（CPU、内存、磁盘、网络）
- ✓ 管理 Docker 容器（启动、停止、重启、删除）
- ✓ 部署新容器
- ✓ 记住密码功能
- ✓ 打开系统终端

## 🔧 故障排除

### 问题 1: 应用闪退

**症状**: 双击应用后立即退出

**解决方案**:
```bash
# 从命令行运行查看详细错误
./dist/CloudManager.app/Contents/MacOS/CloudManager

# 常见错误：缺少模块
# 解决：在 spec 文件的 hiddenimports 中添加缺失模块
```

### 问题 2: 密码加密模块错误

**错误**: `ModuleNotFoundError: No module named 'cryptography.fernet'`

**解决**: 确保 spec 文件包含以下 hiddenimports:
```python
'cryptography',
'cryptography.fernet',
'cryptography.hazmat',
'cryptography.hazmat.primitives',
'cryptography.hazmat.primitives.kdf',
'cryptography.hazmat.primitives.kdf.pbkdf2',
```

### 问题 3: PyYAML 架构不匹配

**错误**: `IncompatibleBinaryArchError: yaml/_yaml.cpython-311-darwin.so`

**解决**: 重新安装对应架构的 PyYAML
```bash
# ARM64
arch -arm64 python -m pip install --force-reinstall PyYAML

# x86_64 (需要 Rosetta)
arch -x86_64 python -m pip install --force-reinstall PyYAML
```

### 问题 4: 图标不显示

**解决**: 确保 `resources/icon.icns` 存在且路径正确
```bash
ls -lh resources/icon.icns
```

## 📊 构建配置对比

| 配置项 | 单架构 | 双架构 |
|--------|--------|--------|
| 构建时间 | ~2 分钟 | ~5 分钟 |
| 应用大小 | ~39MB | ~85MB |
| 兼容性 | 单一架构 | 所有 Mac |
| 启动速度 | 快 | 稍慢 |
| 推荐用途 | 开发测试 | 公开发布 |

## 🚀 分发建议

### 开发阶段
- 使用单架构版本
- 快速迭代测试

### 内部测试
- 根据测试人员机器选择架构
- 或提供双架构版本

### 公开发布
- 提供双架构版本
- 或分别提供 ARM64 和 x86_64 版本供下载

## 📝 Spec 文件配置说明

关键配置项：

```python
hiddenimports=[
    # GUI 框架
    'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
    
    # SSH 和 Docker
    'paramiko', 'docker',
    
    # 加密相关（重要！）
    'cryptography', 'cryptography.fernet',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    
    # YAML 支持
    'yaml', 'PyYAML',
]

datas=[
    ('src/ui', 'ui'),
    ('src/core', 'core'),
    ('src/utils', 'utils'),
]

target_arch='arm64'  # 或 'x86_64' 或 None（自动检测）
```

## 🎯 最佳实践

1. **定期清理构建缓存**
   ```bash
   rm -rf build dist *.spec
   ```

2. **版本控制**
   - 在 Info.plist 中设置版本号
   - 使用有意义的文件名：`CloudManager-v1.0.0-Univeral.app`

3. **代码签名**（可选但推荐）
   ```bash
   codesign --deep --force --sign "Developer ID" dist/CloudManager.app
   ```

4. **公证**（用于公开发布）
   ```bash
   xcrun notarytool submit dist/CloudManager.app --apple-id "your@email.com"
   ```

## 📞 支持

如遇到问题，请查看：
- `UNIVERSAL_BUILD_GUIDE.md` - 详细的双架构构建指南
- 直接运行应用查看错误输出
- 检查 PyInstaller 日志文件
