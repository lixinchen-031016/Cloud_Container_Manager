"""
macOS 风格卡片控件
带圆角、阴影和 hover 效果
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt6.QtGui import QColor


class MacOsCard(QFrame):
    """
    macOS 风格卡片控件
    
    特性：
    - 圆角设计（12px）
    - 优雅的阴影效果
    - hover 时轻微上浮动画
    - 支持深色模式
    - 内置标题和内容区域
    """
    
    def __init__(
        self,
        title: str = "",
        parent=None
    ):
        super().__init__(parent)
        
        self.setObjectName("resourceCard")
        self._is_dark_mode = False
        self._hover_offset = 0.0
        
        # 设置基本属性
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 创建布局
        self._setup_layout(title)
        
        # 创建阴影效果
        self._setup_shadow()
        
        # 创建动画
        self._setup_animation()
        
        # 应用样式
        self._apply_stylesheet()
    
    def _setup_layout(self, title: str):
        """设置布局"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题标签
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("""
                font-weight: 600;
                font-size: 15px;
                color: #1d1d1f;
            """)
            layout.addWidget(self.title_label)
        
        # 内容区域
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)
    
    def _setup_shadow(self):
        """设置阴影效果"""
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(0, 0, 0, 30))
        self.shadow_effect.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow_effect)
    
    def _setup_animation(self):
        """设置动画"""
        self._hover_animation = QPropertyAnimation(self, b"hover_offset")
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._shadow_animation = QPropertyAnimation(self.shadow_effect, b"offset")
        self._shadow_animation.setDuration(200)
        self._shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @pyqtProperty(float)
    def hover_offset(self) -> float:
        """悬停偏移量"""
        return self._hover_offset
    
    @hover_offset.setter
    def hover_offset(self, value: float):
        """设置悬停偏移量"""
        self._hover_offset = value
        # 更新阴影偏移
        new_offset_y = 4 + value * 2
        self.shadow_effect.setOffset(0, new_offset_y)
        self.update()
    
    def set_dark_mode(self, is_dark: bool) -> None:
        """设置是否为深色模式"""
        self._is_dark_mode = is_dark
        self._update_title_color()
        self._apply_stylesheet()
    
    def _update_title_color(self):
        """更新标题颜色"""
        if hasattr(self, 'title_label'):
            color = "#F5F5F7" if self._is_dark_mode else "#1D1D1F"
            self.title_label.setStyleSheet(f"""
                font-weight: 600;
                font-size: 15px;
                color: {color};
            """)
    
    def _apply_stylesheet(self):
        """应用样式表"""
        bg_color = "#2C2C2E" if self._is_dark_mode else "#FFFFFF"
        hover_bg = "#3A3A3C" if self._is_dark_mode else "#FAFAFA"
        
        # 根据 hover 状态调整背景色
        if self._hover_offset > 0:
            # 混合 hover 颜色
            factor = self._hover_offset
            current_bg = self._blend_colors(bg_color, hover_bg, factor)
        else:
            current_bg = bg_color
        
        self.setStyleSheet(f"""
            QFrame#resourceCard {{
                background-color: {current_bg};
                border-radius: 12px;
            }}
        """)
    
    def _blend_colors(self, color1: str, color2: str, factor: float) -> str:
        """混合两种颜色"""
        from PyQt6.QtGui import QColor
        
        c1 = QColor(color1)
        c2 = QColor(color2)
        
        r = int(c1.red() + (c2.red() - c1.red()) * factor)
        g = int(c1.green() + (c2.green() - c1.green()) * factor)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def add_content_widget(self, widget) -> None:
        """添加内容控件"""
        self.content_layout.addWidget(widget)
    
    def enterEvent(self, event) -> None:
        """鼠标进入事件"""
        self._hover_animation.setStartValue(self._hover_offset)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        self._shadow_animation.setStartValue(self.shadow_effect.offset())
        self._shadow_animation.setEndValue(QPoint(0, 6))
        self._shadow_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开事件"""
        self._hover_animation.setStartValue(self._hover_offset)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
        self._shadow_animation.setStartValue(self.shadow_effect.offset())
        self._shadow_animation.setEndValue(QPoint(0, 4))
        self._shadow_animation.start()
        
        super().leaveEvent(event)


class MacOsProgressBar(QFrame):
    """
    macOS 风格进度条
    
    特性：
    - 细进度条（6-8px）
    - 圆角设计
    - 根据值动态变色（绿->橙->红）
    - 支持深色模式
    """
    
    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 100.0,
        parent=None
    ):
        super().__init__(parent)
        
        self._value = value
        self._max_value = max_value
        self._is_dark_mode = False
        
        # 设置固定高度
        self.setFixedHeight(8)
        
        # 创建布局
        self._setup_layout()
        
        # 应用样式
        self._apply_stylesheet()
    
    def _setup_layout(self):
        """设置布局"""
        # 不使用布局，直接绘制
        self.setStyleSheet("""
            background-color: transparent;
        """)
    
    def set_dark_mode(self, is_dark: bool) -> None:
        """设置深色模式"""
        self._is_dark_mode = is_dark
        self._apply_stylesheet()
    
    def set_value(self, value: float) -> None:
        """设置进度值"""
        self._value = value
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        """应用样式表"""
        # 根据值确定背景色
        percent = (self._value / self._max_value) * 100 if self._max_value > 0 else 0
        bg_color = "#3A3A3C" if self._is_dark_mode else "#E8E8ED"
        
        self.setStyleSheet(f"""
            background-color: {bg_color};
            border-radius: 4px;
        """)
        
        # 触发重绘
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        from PyQt6.QtGui import QPainter, QColor, QBrush
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 计算宽度
        percent = min(1.0, self._value / self._max_value) if self._max_value > 0 else 0
        bar_width = int(self.width() * percent)
        
        # 确定颜色
        percent_value = percent * 100
        if percent_value >= 90:
            color = "#FF3B30" if not self._is_dark_mode else "#FF453A"
        elif percent_value >= 70:
            color = "#FF9500" if not self._is_dark_mode else "#FF9F0A"
        else:
            color = "#007AFF" if not self._is_dark_mode else "#0A84FF"
        
        # 绘制前景条
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, bar_width, self.height(), 4, 4)
