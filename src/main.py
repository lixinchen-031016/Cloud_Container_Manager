"""
Cloud Container Manager - 应用入口
云端服务器与容器管理 GUI 应用
"""
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """应用主函数"""
    # 启用高 DPI 支持
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass  # 旧版本 PyQt6 可能不支持
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Container Manager")
    app.setOrganizationName("CloudManager")
    app.setApplicationVersion("1.0.0")
    
    # 设置全局字体
    # 使用系统默认字体，避免字体缺失警告
    font = QFont()
    font.setPointSize(13)
    app.setFont(font)
    
    # 设置应用风格
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
