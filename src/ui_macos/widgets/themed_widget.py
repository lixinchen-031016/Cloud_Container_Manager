"""
主题感知控件基类
所有支持主题切换的控件都应继承此类
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer
from services.theme_service import ThemeService, get_theme_service


class ThemedWidget(QWidget):
    """
    主题感知控件基类
    
    特性：
    - 自动注册到主题服务
    - 主题切换时自动调用 update_theme 方法
    - 提供便捷的颜色访问方法
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._theme_service = get_theme_service()
        self._is_dark_mode = self._theme_service.is_dark_mode()
        
        # 延迟注册到主题服务，确保子类完全初始化
        QTimer.singleShot(0, self._register_with_theme_service)
    
    def _register_with_theme_service(self):
        """延迟注册到主题服务"""
        try:
            self._theme_service.register_widget(self)
        except Exception:
            pass  # 如果注册失败，忽略错误（widget 可能已被销毁）
    
    def update_theme(self, is_dark_mode: bool) -> None:
        """
        主题更新回调
        
        Args:
            is_dark_mode: 是否为深色模式
        """
        self._is_dark_mode = is_dark_mode
        self.on_theme_changed(is_dark_mode)
        self.update()  # 触发重绘
    
    def set_dark_mode(self, is_dark: bool) -> None:
        """设置深色模式（兼容旧接口）"""
        self.update_theme(is_dark)
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """
        主题变化处理（子类重写此方法）
        
        Args:
            is_dark_mode: 是否为深色模式
        """
        pass
    
    def get_color(self, color_name: str) -> str:
        """
        获取当前主题颜色
        
        Args:
            color_name: 颜色名称
            
        Returns:
            颜色 hex 字符串
        """
        return self._theme_service.get_color(color_name)
    
    def get_accent_color(self) -> str:
        """获取强调色"""
        return self._theme_service.get_accent_color()
    
    def get_background_color(self) -> str:
        """获取背景色"""
        return self._theme_service.get_background_color()
    
    def get_card_background_color(self) -> str:
        """获取卡片背景色"""
        return self._theme_service.get_card_background_color()
    
    def get_text_color(self) -> str:
        """获取主要文本颜色"""
        return self._theme_service.get_text_color()
    
    def get_secondary_text_color(self) -> str:
        """获取次要文本颜色"""
        return self._theme_service.get_secondary_text_color()
    
    def closeEvent(self, event):
        """关闭事件 - 注销自己"""
        try:
            self._theme_service.unregister_widget(self)
        except Exception:
            pass
        super().closeEvent(event)
