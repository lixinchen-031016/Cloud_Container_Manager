"""
Cloud Container Manager - macOS UI 版本入口
"""
import sys
import os

# 添加 src 目录到路径
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_path)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from services.theme_service import get_theme_service
from ui_macos.main_window import MainWindow


def main():
    """应用主函数"""
    # 启用高 DPI 支持
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
    app.setApplicationVersion("2.0.0")
    
    # 初始化主题服务
    theme_service = get_theme_service()
    theme_service.initialize()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
