#!/bin/bash
# CloudManager 打包脚本 - 当前架构优化版
# 构建针对当前机器架构优化的应用

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================================="
echo "CloudManager 打包工具"
echo "=================================================="

# 显示当前架构
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo -e "${BLUE}当前架构：ARM64 (Apple Silicon)${NC}"
    TARGET_ARCH="arm64"
else
    echo -e "${BLUE}当前架构：x86_64 (Intel)${NC}"
    TARGET_ARCH="x86_64"
fi

# 清理
rm -rf build dist
source venv/bin/activate

echo -e "\n${YELLOW}开始打包...${NC}"

# 创建 spec 文件
cat > CloudManager.spec << EOF
# -*- mode: python ; coding: utf-8 -*-
# Target Architecture: ${TARGET_ARCH}

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/ui', 'ui'), ('src/core', 'core'), ('src/utils', 'utils')],
    hiddenimports=[
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
        'paramiko', 'docker', 'cryptography',
        'cryptography.fernet', 'cryptography.hazmat',
        'cryptography.hazmat.primitives', 'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'yaml', 'PyYAML',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='CloudManager',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    target_arch='${TARGET_ARCH}',
    icon=['resources/icon.icns'],
)

app = BUNDLE(
    exe,
    name='CloudManager.app',
    icon='resources/icon.icns',
    bundle_identifier='com.cloudmanager.app',
    version='1.0.0',
)
EOF

# 执行打包
pyinstaller --clean CloudManager.spec 2>&1 | tail -10

# 验证结果
echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}✓ 打包成功完成！${NC}"
echo -e "${GREEN}==================================================${NC}"

echo -e "\n${BLUE}应用信息:${NC}"
ls -lh dist/CloudManager.app/Contents/MacOS/CloudManager
echo ""
du -sh dist/CloudManager.app
echo ""

echo -e "${BLUE}架构信息:${NC}"
lipo -info dist/CloudManager.app/Contents/MacOS/CloudManager
echo ""

echo -e "${YELLOW}运行方式:${NC}"
echo "  • 双击打开：open dist/CloudManager.app"
echo "  • 命令行：./dist/CloudManager.app/Contents/MacOS/CloudManager"
echo ""
echo -e "${BLUE}注意：${NC}此应用针对 ${TARGET_ARCH} 架构优化"
if [ "$ARCH" = "arm64" ]; then
    echo "      在 Intel Mac 上需要使用 Rosetta 2 运行"
else
    echo "      在 Apple Silicon Mac 上需要使用 Rosetta 2 运行"
fi
echo ""
