"""
macOS 风格 UI 测试应用
用于测试新创建的 macOS 风格控件和主题服务
"""
import sys
import os

# 添加 src 目录到路径
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_path)

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt

from services.theme_service import get_theme_service
from ui_macos.widgets.macos_button import MacOsButton
from ui_macos.widgets.macos_card import MacOsCard
from ui_macos.widgets.macos_sidebar import MacOsSidebar
from ui_macos.widgets.themed_widget import ThemedWidget


class TestWindow(ThemedWidget):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("macOS UI 测试")
        self.setMinimumSize(1000, 700)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        central_widget = ThemedWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧边栏
        sidebar = MacOsSidebar(title="☁️ 服务器", show_add_button=True, show_search=True)
        sidebar.add_item("服务器 1", data={"id": 1})
        sidebar.add_item("服务器 2", data={"id": 2})
        sidebar.add_item("测试服务器", data={"id": 3})
        main_layout.addWidget(sidebar)
        
        # 右侧内容区域
        content_area = ThemedWidget()
        content_area.setStyleSheet(f"background-color: {self.get_background_color()};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("📊 测试面板")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.get_text_color()};
        """)
        content_layout.addWidget(title_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        primary_btn = MacOsButton("主要按钮", is_primary=True)
        secondary_btn = MacOsButton("次要按钮", is_primary=False)
        
        button_layout.addWidget(primary_btn)
        button_layout.addWidget(secondary_btn)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        # 卡片网格
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # 创建测试卡片
        card1 = MacOsCard("CPU 使用率")
        card1.add_content_widget(QLabel("45.2%"))
        
        card2 = MacOsCard("内存使用")
        card2.add_content_widget(QLabel("8.5 GB / 16 GB"))
        
        card3 = MacOsCard("磁盘空间")
        card3.add_content_widget(QLabel("256 GB / 512 GB"))
        
        card4 = MacOsCard("网络流量")
        card4.add_content_widget(QLabel("↑ 1.2 GB  ↓ 3.4 GB"))
        
        grid.addWidget(card1, 0, 0)
        grid.addWidget(card2, 0, 1)
        grid.addWidget(card3, 1, 0)
        grid.addWidget(card4, 1, 1)
        
        content_layout.addLayout(grid)
        content_layout.addStretch()
        
        content_area.setLayout(content_layout)
        main_layout.addWidget(content_area, 1)
        
        central_widget.setLayout(main_layout)
        
        # 应用主题
        self.on_theme_changed(self._is_dark_mode)
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """主题变化处理"""
        bg_color = self.get_background_color()
        self.centralWidget().setStyleSheet(f"background-color: {bg_color};")


def main():
    """主函数"""
    # 启用高 DPI
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("macOS UI Test")
    app.setOrganizationName("CloudManager")
    
    # 初始化主题服务
    theme_service = get_theme_service()
    theme_service.initialize()
    
    # 创建并显示窗口
    window = TestWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    from PyQt6.QtWidgets import QHBoxLayout
    main()
