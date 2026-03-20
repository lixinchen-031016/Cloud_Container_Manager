"""
macOS 风格按钮控件
支持 Primary/Secondary 样式，带 hover 和 pressed 动画效果
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QEnterEvent
from PyQt6.QtCore import Qt


class MacOsButton(QPushButton):
    """
    macOS 风格按钮
    
    特性：
    - 圆角设计（8px）
    - 平滑的 hover/pressed 过渡动画
    - 支持 Primary/Secondary 两种样式
    - 自动适配深色模式
    """
    
    def __init__(
        self,
        text: str = "",
        is_primary: bool = True,
        parent=None
    ):
        super().__init__(text, parent)
        
        self._is_primary = is_primary
        self._is_dark_mode = False
        self._hover_opacity = 0.0
        
        # 设置基本属性
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        
        # 创建动画
        self._setup_animation()
        
        # 应用初始样式
        self._apply_stylesheet()
    
    def _setup_animation(self):
        """设置动画"""
        self._hover_animation = QPropertyAnimation(self, b"hover_opacity")
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @pyqtProperty(float)
    def hover_opacity(self) -> float:
        """悬停透明度"""
        return self._hover_opacity
    
    @hover_opacity.setter
    def hover_opacity(self, value: float):
        """设置悬停透明度"""
        self._hover_opacity = value
        self._apply_stylesheet()
    
    def set_dark_mode(self, is_dark: bool) -> None:
        """设置是否为深色模式"""
        self._is_dark_mode = is_dark
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        """应用样式表"""
        if self._is_primary:
            base_color = "#0A84FF" if self._is_dark_mode else "#007AFF"
            
            # 计算 hover 颜色（混合白色）
            hover_color = self._blend_colors(base_color, "#FFFFFF", 0.15 + self._hover_opacity * 0.15)
            pressed_color = self._blend_colors(base_color, "#FFFFFF", 0.25)
        else:
            base_color = "#3A3A3C" if self._is_dark_mode else "#F5F5F7"
            
            # 计算 hover 颜色（混合黑色）
            hover_color = self._blend_colors(base_color, "#000000", 0.05 + self._hover_opacity * 0.1)
            pressed_color = self._blend_colors(base_color, "#000000", 0.15)
        
        text_color = "#FFFFFF" if (self._is_primary or not self._is_dark_mode) else "#1D1D1F"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                color: {text_color};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            
            QPushButton:disabled {{
                background-color: {"#5A5A5C" if self._is_dark_mode else "#D1D1D6"};
                color: {"#8E8E90" if self._is_dark_mode else "#8E8E93"};
            }}
        """)
    
    def _blend_colors(self, color1: str, color2: str, factor: float) -> str:
        """
        混合两种颜色
        
        Args:
            color1: 颜色 1（hex）
            color2: 颜色 2（hex）
            factor: 混合因子（0-1）
            
        Returns:
            混合后的颜色（hex）
        """
        c1 = QColor(color1)
        c2 = QColor(color2)
        
        r = int(c1.red() + (c2.red() - c1.red()) * factor)
        g = int(c1.green() + (c2.green() - c1.green()) * factor)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def enterEvent(self, event: QEnterEvent) -> None:
        """鼠标进入事件"""
        if not self.isEnabled():
            return
        
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开事件"""
        if not self.isEnabled():
            return
        
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件"""
        if not self.isEnabled():
            return
        
        # 立即显示 pressed 状态
        self._hover_opacity = 1.0
        self._apply_stylesheet()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件"""
        if not self.isEnabled():
            return
        
        # 恢复 hover 状态
        self._hover_opacity = 0.0
        self._apply_stylesheet()
        super().mouseReleaseEvent(event)
