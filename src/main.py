"""
Cloud Container Manager - 应用入口
云端服务器与容器管理 GUI 应用
"""
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QFont, QPalette, QColor

from ui.main_window import MainWindow


def setup_macos_style(app: QApplication) -> None:
    """设置 macOS 原生风格"""
    # 启用高 DPI 支持
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass
    
    # 使用 macOS 原生风格
    app.setStyle("Fusion")
    
    # 设置调色板（macOS 风格）
    palette = QPalette()
    
    # 基础颜色
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 30))
    
    # 按钮颜色
    palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 30, 30))
    
    # 高亮颜色（macOS 蓝色）
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # 链接颜色
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 255))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(0, 122, 255))
    
    # 禁用状态
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(180, 180, 180))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(180, 180, 180))
    
    app.setPalette(palette)
    
    # 设置全局字体（使用系统字体）
    font = QFont(".SF NS Text", 13)  # macOS 系统字体
    if not QFont(".SF NS Text").exactMatch():
        font = QFont(".Helvetica Neue DeskInterface", 13)
    app.setFont(font)


def main():
    """应用主函数"""
    # 启用高 DPI 支持（必须在创建 QApplication 之前）
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Container Manager")
    app.setOrganizationName("CloudManager")
    app.setApplicationVersion("1.0.5")
    
    # 设置 macOS 风格
    setup_macos_style(app)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
