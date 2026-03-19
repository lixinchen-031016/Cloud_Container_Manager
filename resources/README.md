# 应用图标说明

## 当前状态

`resources/icon.icns` 文件是一个占位符。要使用自定义图标，请按照以下步骤操作：

## 创建 .icns 图标文件

### 方法 1: 使用在线转换工具

1. 准备一个 PNG 图标文件（建议尺寸：1024x1024）
2. 访问在线转换网站，如：
   - https://cloudconvert.com/png-to-icns
   - https://iconverticons.com/online/
3. 上传 PNG 文件并转换为 .icns 格式
4. 将生成的 `icon.icns` 文件替换到 `resources/` 目录

### 方法 2: 使用 macOS 命令行工具

```bash
# 准备图标源文件（PNG 格式，1024x1024）
# 创建 icon.iconset 目录
mkdir icon.iconset

# 生成各种尺寸的图标
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
sips -z 64 64 icon.png --out icon.iconset/icon_64x64.png
sips -z 32 32 icon.png --out icon.iconset/icon_32x32.png
sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png

# 创建 @2x 版本
cp icon.iconset/icon_256x256.png icon.iconset/icon_128x128@2x.png
cp icon.iconset/icon_512x512.png icon.iconset/icon_256x256@2x.png
cp icon.iconset/icon_512x512.png icon.iconset/icon_512x512@2x.png

# 转换为 .icns 格式
iconutil -c icns icon.iconset -o resources/icon.icns

# 清理临时目录
rm -rf icon.iconset
```

### 方法 3: 使用 Sketch/Figma

1. 在 Sketch 或 Figma 中设计 1024x1024 的图标
2. 导出为 PNG 格式
3. 使用方法 1 或方法 2 转换为 .icns

## 推荐图标尺寸

macOS 需要以下尺寸的图标（包含在 .icns 文件中）：
- 16x16
- 32x32
- 64x64
- 128x128
- 256x256
- 512x512
- 1024x1024

## 不使用图标的情况

如果不需要自定义图标，可以：

1. 删除 build_app.sh 中的 `--icon "resources/icon.icns"` 参数
2. PyInstaller 会使用默认的应用图标

修改后的命令：
```bash
pyinstaller --name "CloudManager" \
    --windowed \
    --onefile \
    --osx-bundle-identifier "com.cloudmanager.app" \
    --hidden-import PyQt6 \
    --hidden-import paramiko \
    --hidden-import docker \
    --noconfirm \
    src/main.py
```
