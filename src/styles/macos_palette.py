"""
macOS 颜色调色板
定义浅色和深色模式下的颜色方案
"""
from PyQt6.QtGui import QColor


class MacOsPalette:
    """
    macOS Big Sur/Monterey 颜色调色板
    
    包含浅色模式和深色模式的所有标准颜色
    """
    
    # ========== 浅色模式颜色 ==========
    
    # 背景色
    LIGHT_WINDOW_BG = "#F5F5F7"      # 主窗口背景
    LIGHT_CARD_BG = "#FFFFFF"         # 卡片背景
    LIGHT_SIDEBAR_BG = "#FFFFFF"      # 侧边栏背景
    
    # 文本色
    LIGHT_TEXT_PRIMARY = "#1D1D1F"    # 主要文本
    LIGHT_TEXT_SECONDARY = "#86868B"  # 次要文本
    LIGHT_TEXT_DISABLED = "#C7C7CC"   # 禁用文本
    
    # 强调色
    LIGHT_ACCENT_BLUE = "#007AFF"     # macOS 蓝
    LIGHT_ACCENT_GREEN = "#34C759"    # 成功绿
    LIGHT_ACCENT_ORANGE = "#FF9500"   # 警告橙
    LIGHT_ACCENT_RED = "#FF3B30"      # 危险红
    
    # 边框和分隔线
    LIGHT_BORDER = "#E0E0E0"          # 边框
    LIGHT_SEPARATOR = "#E5E5EA"       # 分隔线
    
    # 交互状态
    LIGHT_HOVER = "rgba(0, 122, 255, 0.08)"   # 悬停
    LIGHT_SELECTED = "#E8F2FF"                # 选中背景
    LIGHT_PRESSED = "rgba(0, 122, 255, 0.15)" # 按下
    
    # ========== 深色模式颜色 ==========
    
    # 背景色
    DARK_WINDOW_BG = "#1E1E1E"        # 主窗口背景
    DARK_CARD_BG = "#2C2C2E"          # 卡片背景
    DARK_SIDEBAR_BG = "#2C2C2E"       # 侧边栏背景
    
    # 文本色
    DARK_TEXT_PRIMARY = "#F5F5F7"     # 主要文本
    DARK_TEXT_SECONDARY = "#98989D"   # 次要文本
    DARK_TEXT_DISABLED = "#48484A"    # 禁用文本
    
    # 强调色
    DARK_ACCENT_BLUE = "#0A84FF"      # macOS 蓝（深色更亮）
    DARK_ACCENT_GREEN = "#30D158"     # 成功绿
    DARK_ACCENT_ORANGE = "#FF9F0A"    # 警告橙
    DARK_ACCENT_RED = "#FF453A"       # 危险红
    
    # 边框和分隔线
    DARK_BORDER = "#38383A"           # 边框
    DARK_SEPARATOR = "#38383A"        # 分隔线
    
    # 交互状态
    DARK_HOVER = "rgba(10, 132, 255, 0.12)"   # 悬停
    DARK_SELECTED = "rgba(10, 132, 255, 0.2)" # 选中背景
    DARK_PRESSED = "rgba(10, 132, 255, 0.25)" # 按下
    
    # ========== 语义化颜色 ==========
    
    # 根据使用场景分类的颜色
    SUCCESS_LIGHT = "#34C759"
    SUCCESS_DARK = "#30D158"
    
    WARNING_LIGHT = "#FF9500"
    WARNING_DARK = "#FF9F0A"
    
    ERROR_LIGHT = "#FF3B30"
    ERROR_DARK = "#FF453A"
    
    INFO_LIGHT = "#007AFF"
    INFO_DARK = "#0A84FF"
    
    # ========== 辅助方法 ==========
    
    @staticmethod
    def get_color(color_name: str, is_dark_mode: bool = False) -> QColor:
        """
        获取颜色
        
        Args:
            color_name: 颜色名称（不含前缀）
            is_dark_mode: 是否为深色模式
            
        Returns:
            QColor 对象
        """
        prefix = "DARK_" if is_dark_mode else "LIGHT_"
        full_name = f"{prefix}{color_name}"
        
        color_hex = getattr(MacOsPalette, full_name, None)
        if color_hex is None:
            raise ValueError(f"未知颜色：{full_name}")
        
        return QColor(color_hex)
    
    @staticmethod
    def get_accent_color(is_dark_mode: bool = False) -> QColor:
        """获取强调色（蓝色）"""
        return MacOsPalette.get_color("ACCENT_BLUE", is_dark_mode)
    
    @staticmethod
    def get_background_color(is_dark_mode: bool = False) -> QColor:
        """获取背景色"""
        return MacOsPalette.get_color("WINDOW_BG", is_dark_mode)
    
    @staticmethod
    def get_card_background_color(is_dark_mode: bool = False) -> QColor:
        """获取卡片背景色"""
        return MacOsPalette.get_color("CARD_BG", is_dark_mode)
    
    @staticmethod
    def get_text_color(is_dark_mode: bool = False) -> QColor:
        """获取主要文本颜色"""
        return MacOsPalette.get_color("TEXT_PRIMARY", is_dark_mode)
    
    @staticmethod
    def get_secondary_text_color(is_dark_mode: bool = False) -> QColor:
        """获取次要文本颜色"""
        return MacOsPalette.get_color("TEXT_SECONDARY", is_dark_mode)
