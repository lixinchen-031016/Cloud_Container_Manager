"""
主题管理服务
管理应用的主题切换和颜色方案
"""
from typing import List, Callable, Any
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal
from services.system_theme_detector import SystemThemeDetector
from styles.macos_palette import MacOsPalette


class ThemeService(QObject):
    """
    主题管理服务
    
    特性：
    - 自动跟随系统深色/浅色模式
    - 支持手动切换主题
    - 通知所有注册的 UI 组件
    - 提供统一的颜色访问接口
    """
    
    # 主题变化信号
    theme_changed = pyqtSignal(bool)  # is_dark_mode
    
    def __init__(self):
        super().__init__()
        self._is_dark_mode = False
        self._theme_widgets: List[Any] = []
        self._detector = SystemThemeDetector.get_instance()
        
        # 初始化时检测当前主题
        self._is_dark_mode = self._detector.is_dark_mode()
    
    def initialize(self) -> None:
        """初始化主题服务"""
        # 开始监听系统主题变化
        self._detector.start_listening(self._on_system_theme_changed)
        print(f"[ThemeService] 初始化完成，当前主题：{'深色' if self._is_dark_mode else '浅色'}")
    
    def cleanup(self) -> None:
        """清理资源"""
        self._detector.stop_listening()
        self._theme_widgets.clear()
    
    def _on_system_theme_changed(self, is_dark: bool) -> None:
        """系统主题变化回调"""
        self.set_theme('dark' if is_dark else 'light')
    
    def set_theme(self, theme: str) -> None:
        """
        设置主题
        
        Args:
            theme: 'light' 或 'dark'
        """
        if theme not in ['light', 'dark']:
            raise ValueError("theme 必须是 'light' 或 'dark'")
        
        new_is_dark = theme == 'dark'
        
        if new_is_dark == self._is_dark_mode:
            return  # 主题未变化
        
        self._is_dark_mode = new_is_dark
        print(f"[ThemeService] 切换主题：{'深色' if self._is_dark_mode else '浅色'}")
        
        # 发射主题变化信号
        self.theme_changed.emit(self._is_dark_mode)
        
        # 更新所有注册的控件
        self._update_all_widgets()
    
    def is_dark_mode(self) -> bool:
        """获取当前是否为深色模式"""
        return self._is_dark_mode
    
    def get_color(self, color_name: str) -> str:
        """
        获取颜色值（hex 字符串）
        
        Args:
            color_name: 颜色名称（不含前缀），如 "WINDOW_BG"
            
        Returns:
            颜色 hex 字符串
        """
        return getattr(MacOsPalette, f"DARK_{color_name}" if self._is_dark_mode else f"LIGHT_{color_name}")
    
    def get_accent_color(self) -> str:
        """获取强调色"""
        return self.get_color("ACCENT_BLUE")
    
    def get_background_color(self) -> str:
        """获取背景色"""
        return self.get_color("WINDOW_BG")
    
    def get_card_background_color(self) -> str:
        """获取卡片背景色"""
        return self.get_color("CARD_BG")
    
    def get_text_color(self) -> str:
        """获取主要文本颜色"""
        return self.get_color("TEXT_PRIMARY")
    
    def get_secondary_text_color(self) -> str:
        """获取次要文本颜色"""
        return self.get_color("TEXT_SECONDARY")
    
    def register_widget(self, widget: Any) -> None:
        """
        注册主题感知控件
        
        Args:
            widget: 实现了 set_dark_mode(bool) 方法的控件
        """
        if widget not in self._theme_widgets:
            self._theme_widgets.append(widget)
            
            # 立即应用当前主题
            if hasattr(widget, 'set_dark_mode'):
                widget.set_dark_mode(self._is_dark_mode)
    
    def unregister_widget(self, widget: Any) -> None:
        """注销控件"""
        if widget in self._theme_widgets:
            self._theme_widgets.remove(widget)
    
    def _update_all_widgets(self) -> None:
        """更新所有注册的控件"""
        for widget in self._theme_widgets:
            try:
                if hasattr(widget, 'set_dark_mode'):
                    widget.set_dark_mode(self._is_dark_mode)
                elif hasattr(widget, 'update_theme'):
                    widget.update_theme(self._is_dark_mode)
            except Exception as e:
                print(f"[ThemeService] 更新控件失败：{e}")


# 全局主题服务实例
_global_theme_service: ThemeService = None


def get_theme_service() -> ThemeService:
    """获取全局主题服务实例"""
    global _global_theme_service
    if _global_theme_service is None:
        _global_theme_service = ThemeService()
    return _global_theme_service
