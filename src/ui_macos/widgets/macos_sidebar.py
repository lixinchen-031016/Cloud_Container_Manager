"""
macOS 风格侧边栏控件
支持分组、搜索和自定义项渲染
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class MacOsSidebar(QWidget):
    """
    macOS 风格侧边栏
    
    特性：
    - 圆角项设计（6px）
    - 平滑的 hover/selected 效果
    - 支持搜索过滤
    - 支持分组标题
    - 自动适配深色模式
    """
    
    # 信号
    item_selected = pyqtSignal(object)  # 选中项数据
    add_button_clicked = pyqtSignal()   # 添加按钮点击
    
    def __init__(
        self,
        title: str = "服务器",
        show_add_button: bool = True,
        show_search: bool = True,
        parent=None
    ):
        super().__init__(parent)
        
        self.setObjectName("sidebar")
        self._is_dark_mode = False
        
        # 设置基本属性
        self.setMaximumWidth(280)
        self.setMinimumWidth(220)
        
        # 创建布局
        self._setup_layout(title, show_add_button, show_search)
        
        # 应用样式
        self._apply_stylesheet()
    
    def _setup_layout(self, title: str, show_add_button: bool, show_search: bool):
        """设置布局"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题区域
        title_label = QLabel(title)
        title_label.setObjectName("sidebarTitle")
        title_label.setStyleSheet(self._get_title_stylesheet())
        layout.addWidget(title_label)
        
        # 搜索框（可选）
        if show_search:
            self.search_input = MacOsSearchBox()
            self.search_input.textChanged.connect(self._filter_items)
            layout.addWidget(self.search_input)
        
        # 添加按钮（可选）
        if show_add_button:
            self.add_button = QPushButton("+ 添加")
            self.add_button.setObjectName("addServerBtn")
            self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.add_button.setFixedHeight(36)
            self.add_button.clicked.connect(self.add_button_clicked.emit)
            layout.addWidget(self.add_button)
            
            # 按钮底部间距
            spacing_widget = QWidget()
            spacing_widget.setFixedHeight(15)
            layout.addWidget(spacing_widget)
        
        # 列表区域
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("serverList")
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        
        # 移除默认边框和背景
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
                padding: 0 10px;
            }
        """)
        
        layout.addWidget(self.list_widget)
        
        self.setLayout(layout)
    
    def _get_title_stylesheet(self) -> str:
        """获取标题样式表"""
        color = "#F5F5F7" if self._is_dark_mode else "#1D1D1F"
        return f"""
            color: {color};
            font-size: 20px;
            font-weight: 600;
            padding: 20px 15px 10px 15px;
        """
    
    def _apply_stylesheet(self):
        """应用样式表"""
        bg_color = "#2C2C2E" if self._is_dark_mode else "#FFFFFF"
        border_color = "#38383A" if self._is_dark_mode else "#E0E0E0"
        
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {bg_color};
                border-right: 1px solid {border_color};
            }}
        """)
        
        # 更新标题颜色
        title_label = self.findChild(QLabel, "")
        if title_label:
            title_label.setStyleSheet(self._get_title_stylesheet())
    
    def set_dark_mode(self, is_dark: bool) -> None:
        """设置深色模式"""
        self._is_dark_mode = is_dark
        self._apply_stylesheet()
    
    def add_item(
        self,
        text: str,
        data: object = None,
        icon: str = None
    ) -> QListWidgetItem:
        """
        添加列表项
        
        Args:
            text: 显示文本
            data: 关联数据
            icon: 图标（暂不支持）
            
        Returns:
            列表项对象
        """
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, data)
        
        # 设置项的大小
        item.setSizeHint(item.sizeHint().expandedTo(QListWidgetItem().sizeHint()))
        
        self.list_widget.addItem(item)
        return item
    
    def remove_item(self, index: int) -> None:
        """删除列表项"""
        if 0 <= index < self.list_widget.count():
            self.list_widget.takeItem(index)
    
    def clear_items(self) -> None:
        """清空所有列表项"""
        self.list_widget.clear()
    
    def get_selected_item(self) -> tuple[QListWidgetItem, object]:
        """
        获取选中的项
        
        Returns:
            (item, data) 元组
        """
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            return item, data
        return None, None
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """列表项点击事件"""
        data = item.data(Qt.ItemDataRole.UserRole)
        self.item_selected.emit(data)
    
    def _filter_items(self, text: str) -> None:
        """过滤列表项"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def _show_context_menu(self, pos) -> None:
        """显示右键菜单（由外部实现）"""
        # 这个方法可以由外部重写
        pass
    
    def _apply_item_styles(self) -> None:
        """应用列表项样式"""
        selected_bg = "rgba(10, 132, 255, 0.2)" if self._is_dark_mode else "#E8F2FF"
        selected_text = "#0A84FF" if self._is_dark_mode else "#007AFF"
        hover_bg = "#3A3A3C" if self._is_dark_mode else "#F5F5F7"
        text_color = "#F5F5F7" if self._is_dark_mode else "#1D1D1F"
        
        self.list_widget.setStyleSheet(f"""
            QListWidget#serverList {{
                border: none;
                background-color: transparent;
                outline: none;
                padding: 0 10px;
            }}
            
            QListWidget#serverList::item {{
                padding: 12px 15px;
                margin: 2px 0;
                border-radius: 6px;
                color: {text_color};
                font-size: 14px;
            }}
            
            QListWidget#serverList::item:selected {{
                background-color: {selected_bg};
                color: {selected_text};
                font-weight: 500;
            }}
            
            QListWidget#serverList::item:hover {{
                background-color: {hover_bg};
            }}
        """)


class MacOsSearchBox(QLineEdit):
    """
    macOS 风格搜索框
    
    特性：
    - 圆角设计（8px）
    - 半透明背景
    - 内置搜索图标（使用 Unicode 字符）
    - 支持深色模式
    """
    
    def __init__(self, placeholder: str = "搜索...", parent=None):
        super().__init__(parent)
        
        self._is_dark_mode = False
        
        # 设置占位符
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(36)
        
        # 应用样式
        self._apply_stylesheet()
    
    def set_dark_mode(self, is_dark: bool) -> None:
        """设置深色模式"""
        self._is_dark_mode = is_dark
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        """应用样式表"""
        bg_color = "rgba(58, 58, 60, 0.5)" if self._is_dark_mode else "rgba(118, 118, 128, 0.12)"
        text_color = "#F5F5F7" if self._is_dark_mode else "#1D1D1F"
        placeholder_color = "#98989D" if self._is_dark_mode else "#86868B"
        border_color = "rgba(118, 118, 128, 0.2)" if self._is_dark_mode else "rgba(0, 0, 0, 0.1)"
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 8px 12px 8px 32px;
                font-size: 13px;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {"#0A84FF" if self._is_dark_mode else "#007AFF"};
            }}
            
            QLineEdit::placeholder {{
                color: {placeholder_color};
            }}
        """)
