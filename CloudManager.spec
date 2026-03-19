# -*- mode: python ; coding: utf-8 -*-
# Target Architecture: arm64

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
    target_arch='arm64',
    icon=['resources/icon.icns'],
)

app = BUNDLE(
    exe,
    name='CloudManager.app',
    icon='resources/icon.icns',
    bundle_identifier='com.cloudmanager.app',
    version='1.0.0',
)
