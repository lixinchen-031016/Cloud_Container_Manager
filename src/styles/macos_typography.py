"""
macOS 字体排印规范
定义系统字体、字号和字重
"""
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class MacOsTypography:
    """
    macOS 字体排印规范
    
    使用 SF Pro Text 系统字体，定义标准字号和字重
    """
    
    # ========== 字体族 ==========
    
    # macOS 系统字体（按优先级）
    SYSTEM_FONT_FAMILY = ".SF NS Text"
    FALLBACK_FONT_FAMILY = ".Helvetica Neue DeskInterface"
    SECOND_FALLBACK = "Arial"
    
    # ========== 字号规范（以点为单位）==========
    
    # 标题字号
    LARGE_TITLE_SIZE = 34           # 大标题
    TITLE_1_SIZE = 28               # 一级标题
    TITLE_2_SIZE = 22               # 二级标题
    TITLE_3_SIZE = 20               # 三级标题
    
    # 正文字号
    HEADLINE_SIZE = 17              # 重要文本
    BODY_SIZE = 13                  # 标准正文
    CALL_OUT_SIZE = 16              # 标注
    SUBHEAD_SIZE = 15               # 副标题
    
    # 辅助字号
    CAPTION_1_SIZE = 12             # 说明文字 1
    CAPTION_2_SIZE = 11             # 说明文字 2
    FOOTNOTE_SIZE = 13              # 脚注
    BUTTON_SIZE = 13                # 按钮文字
    
    # ========== 字重 ==========
    
    WEIGHT_REGULAR = QFont.Weight.Normal      # 常规
    WEIGHT_MEDIUM = QFont.Weight.Medium       # 中等
    WEIGHT_SEMIBOLD = QFont.Weight.DemiBold   # 半粗体
    WEIGHT_BOLD = QFont.Weight.Bold           # 粗体
    
    # ========== 字体创建方法 ==========
    
    @staticmethod
    def create_font(
        size: int = BODY_SIZE,
        weight: QFont.Weight = WEIGHT_REGULAR,
        italic: bool = False
    ) -> QFont:
        """
        创建系统字体
        
        Args:
            size: 字号
            weight: 字重
            italic: 是否斜体
            
        Returns:
            QFont 对象
        """
        font = QFont(MacOsTypography.SYSTEM_FONT_FAMILY, size)
        font.setWeight(weight)
        font.setItalic(italic)
        
        # 如果首选字体不可用，使用备用字体
        if not font.exactMatch():
            font = QFont(MacOsTypography.FALLBACK_FONT_FAMILY, size)
            font.setWeight(weight)
            font.setItalic(italic)
            
            if not font.exactMatch():
                font = QFont(MacOsTypography.SECOND_FALLBACK, size)
                font.setWeight(weight)
                font.setItalic(italic)
        
        return font
    
    @staticmethod
    def large_title_font() -> QFont:
        """大标题字体"""
        return MacOsTypography.create_font(
            MacOsTypography.LARGE_TITLE_SIZE,
            MacOsTypography.WEIGHT_BOLD
        )
    
    @staticmethod
    def title_1_font() -> QFont:
        """一级标题字体"""
        return MacOsTypography.create_font(
            MacOsTypography.TITLE_1_SIZE,
            MacOsTypography.WEIGHT_BOLD
        )
    
    @staticmethod
    def title_2_font() -> QFont:
        """二级标题字体"""
        return MacOsTypography.create_font(
            MacOsTypography.TITLE_2_SIZE,
            MacOsTypography.WEIGHT_SEMIBOLD
        )
    
    @staticmethod
    def title_3_font() -> QFont:
        """三级标题字体"""
        return MacOsTypography.create_font(
            MacOsTypography.TITLE_3_SIZE,
            MacOsTypography.WEIGHT_SEMIBOLD
        )
    
    @staticmethod
    def headline_font() -> QFont:
        """重要文本字体"""
        return MacOsTypography.create_font(
            MacOsTypography.HEADLINE_SIZE,
            MacOsTypography.WEIGHT_SEMIBOLD
        )
    
    @staticmethod
    def body_font() -> QFont:
        """标准正文字体"""
        return MacOsTypography.create_font(
            MacOsTypography.BODY_SIZE,
            MacOsTypography.WEIGHT_REGULAR
        )
    
    @staticmethod
    def call_out_font() -> QFont:
        """标注字体"""
        return MacOsTypography.create_font(
            MacOsTypography.CALL_OUT_SIZE,
            MacOsTypography.WEIGHT_REGULAR
        )
    
    @staticmethod
    def subhead_font() -> QFont:
        """副标题字体"""
        return MacOsTypography.create_font(
            MacOsTypography.SUBHEAD_SIZE,
            MacOsTypography.WEIGHT_REGULAR
        )
    
    @staticmethod
    def caption_1_font() -> QFont:
        """说明文字 1 字体"""
        return MacOsTypography.create_font(
            MacOsTypography.CAPTION_1_SIZE,
            MacOsTypography.WEIGHT_REGULAR
        )
    
    @staticmethod
    def caption_2_font() -> QFont:
        """说明文字 2 字体"""
        return MacOsTypography.create_font(
            MacOsTypography.CAPTION_2_SIZE,
            MacOsTypography.WEIGHT_REGULAR
        )
    
    @staticmethod
    def button_font() -> QFont:
        """按钮字体"""
        return MacOsTypography.create_font(
            MacOsTypography.BUTTON_SIZE,
            MacOsTypography.WEIGHT_MEDIUM
        )
