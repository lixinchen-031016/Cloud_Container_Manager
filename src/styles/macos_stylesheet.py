"""
macOS 风格样式表生成器
提供统一的样式表生成方法
"""
from typing import Optional


class MacOsStylesheet:
    """
    macOS 样式表生成器
    
    提供常用组件的 macOS 风格样式表
    """
    
    # ========== 通用样式片段 ==========
    
    LIGHT_MODE_COLORS = """
        /* 浅色模式颜色变量 */
        --window-bg: #F5F5F7;
        --card-bg: #FFFFFF;
        --sidebar-bg: #FFFFFF;
        --text-primary: #1D1D1F;
        --text-secondary: #86868B;
        --text-disabled: #C7C7CC;
        --accent-blue: #007AFF;
        --accent-green: #34C759;
        --accent-orange: #FF9500;
        --accent-red: #FF3B30;
        --border: #E0E0E0;
        --separator: #E5E5EA;
        --hover: rgba(0, 122, 255, 0.08);
        --selected: #E8F2FF;
        --pressed: rgba(0, 122, 255, 0.15);
    """
    
    DARK_MODE_COLORS = """
        /* 深色模式颜色变量 */
        --window-bg: #1E1E1E;
        --card-bg: #2C2C2E;
        --sidebar-bg: #2C2C2E;
        --text-primary: #F5F5F7;
        --text-secondary: #98989D;
        --text-disabled: #48484A;
        --accent-blue: #0A84FF;
        --accent-green: #30D158;
        --accent-orange: #FF9F0A;
        --accent-red: #FF453A;
        --border: #38383A;
        --separator: #38383A;
        --hover: rgba(10, 132, 255, 0.12);
        --selected: rgba(10, 132, 255, 0.2);
        --pressed: rgba(10, 132, 255, 0.25);
    """
    
    @staticmethod
    def get_button_stylesheet(
        is_primary: bool = True,
        is_dark_mode: bool = False
    ) -> str:
        """
        获取按钮样式表
        
        Args:
            is_primary: 是否为主要按钮
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        if is_primary:
            bg_color = "#0A84FF" if is_dark_mode else "#007AFF"
            hover_color = "#409CFF" if is_dark_mode else "#005ecb"
            pressed_color = "#66ABFF" if is_dark_mode else "#0051b3"
        else:
            bg_color = "#3A3A3C" if is_dark_mode else "#F5F5F7"
            hover_color = "#48484A" if is_dark_mode else "#E8E8ED"
            pressed_color = "#5A5A5C" if is_dark_mode else "#D1D1D6"
        
        text_color = "#FFFFFF" if (is_primary or not is_dark_mode) else "#1D1D1F"
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
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
                background-color: {"#5A5A5C" if is_dark_mode else "#D1D1D6"};
                color: {"#8E8E90" if is_dark_mode else "#8E8E93"};
            }}
        """
    
    @staticmethod
    def get_card_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取卡片样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        bg_color = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        hover_color = "#3A3A3C" if is_dark_mode else "#FAFAFA"
        
        return f"""
            QFrame#resourceCard {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
            
            QFrame#resourceCard:hover {{
                background-color: {hover_color};
            }}
        """
    
    @staticmethod
    def get_progress_bar_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取进度条样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        track_color = "#3A3A3C" if is_dark_mode else "#E8E8ED"
        
        return f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                text-align: center;
                background-color: {track_color};
                height: 8px;
            }}
            
            QProgressBar::chunk {{
                background-color: {"#0A84FF" if is_dark_mode else "#007AFF"};
                border-radius: 6px;
            }}
            
            QProgressBar::text {{
                color: transparent;
            }}
        """
    
    @staticmethod
    def get_sidebar_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取侧边栏样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        bg_color = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        border_color = "#38383A" if is_dark_mode else "#E0E0E0"
        selected_bg = "rgba(10, 132, 255, 0.2)" if is_dark_mode else "#E8F2FF"
        selected_text = "#0A84FF" if is_dark_mode else "#007AFF"
        hover_bg = "#3A3A3C" if is_dark_mode else "#F5F5F7"
        
        return f"""
            QWidget#sidebar {{
                background-color: {bg_color};
                border-right: 1px solid {border_color};
            }}
            
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
                color: {"#F5F5F7" if is_dark_mode else "#1D1D1F"};
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
        """
    
    @staticmethod
    def get_table_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取表格样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        bg_color = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        alternate_bg = "#3A3A3C" if is_dark_mode else "#FAFAFA"
        header_bg = "#3A3A3C" if is_dark_mode else "#F5F5F7"
        border_color = "#38383A" if is_dark_mode else "#E0E0E0"
        gridline_color = "#3A3A3C" if is_dark_mode else "#F5F5F7"
        selected_bg = "rgba(10, 132, 255, 0.2)" if is_dark_mode else "#E8F2FF"
        selected_text = "#0A84FF" if is_dark_mode else "#007AFF"
        header_text = "#98989D" if is_dark_mode else "#86868B"
        
        return f"""
            QTableWidget {{
                border: 1px solid {border_color};
                border-radius: 8px;
                gridline-color: {gridline_color};
                background-color: {bg_color};
                alternate-background-color: {alternate_bg};
            }}
            
            QTableWidget::item {{
                padding: 10px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {selected_bg};
                color: {selected_text};
            }}
            
            QHeaderView::section {{
                background-color: {header_bg};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {border_color};
                font-weight: 600;
                color: {header_text};
                font-size: 12px;
                text-transform: uppercase;
            }}
        """
    
    @staticmethod
    def get_tab_widget_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取标签页组件样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        bg_color = "#1E1E1E" if is_dark_mode else "#F5F5F7"
        pane_bg = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        tab_text = "#98989D" if is_dark_mode else "#86868B"
        selected_tab_bg = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        selected_tab_text = "#0A84FF" if is_dark_mode else "#007AFF"
        hover_bg = "rgba(10, 132, 255, 0.08)" if is_dark_mode else "rgba(0, 122, 255, 0.08)"
        
        return f"""
            QTabWidget#mainTabs {{
                background-color: {bg_color};
                border: none;
            }}
            
            QTabWidget#mainTabs::pane {{
                border: none;
                background-color: {pane_bg};
                border-radius: 12px;
                padding: 0px;
            }}
            
            QTabWidget#mainTabs::tab-bar {{
                alignment: left;
                left: 20px;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {tab_text};
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 24px;
                margin-right: 4px;
                font-size: 13px;
                font-weight: 500;
                min-width: 100px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {selected_tab_bg};
                color: {selected_tab_text};
                font-weight: 600;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {hover_bg};
                color: {"#F5F5F7" if is_dark_mode else "#1D1D1F"};
            }}
        """
    
    @staticmethod
    def get_main_window_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取主窗口样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        window_bg = "#1E1E1E" if is_dark_mode else "#F5F5F7"
        menubar_bg = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        border_color = "#38383A" if is_dark_mode else "#E0E0E0"
        statusbar_bg = "#2C2C2E" if is_dark_mode else "#FFFFFF"
        menu_item_hover = "#0A84FF" if is_dark_mode else "#007AFF"
        
        return f"""
            QMainWindow {{
                background-color: {window_bg};
            }}
            
            QMenuBar {{
                background-color: {menubar_bg};
                border-bottom: 1px solid {border_color};
                padding: 4px 10px;
            }}
            
            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: 6px;
                background-color: transparent;
            }}
            
            QMenuBar::item:selected {{
                background-color: {"#3A3A3C" if is_dark_mode else "#F5F5F7"};
            }}
            
            QMenu {{
                background-color: {menubar_bg};
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 8px 0;
            }}
            
            QMenu::item {{
                padding: 8px 20px;
                margin: 2px 10px;
                border-radius: 6px;
            }}
            
            QMenu::item:selected {{
                background-color: {menu_item_hover};
                color: white;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {border_color};
                margin: 6px 10px;
            }}
            
            QStatusBar {{
                background-color: {statusbar_bg};
                border-top: 1px solid {border_color};
                color: {"#98989D" if is_dark_mode else "#86868B"};
                font-size: 12px;
            }}
        """
    
    @staticmethod
    def get_scrollbar_stylesheet(is_dark_mode: bool = False) -> str:
        """
        获取滚动条样式表
        
        Args:
            is_dark_mode: 是否为深色模式
            
        Returns:
            样式表字符串
        """
        handle_color = "#48484A" if is_dark_mode else "#D1D1D6"
        handle_hover = "#5A5A5C" if is_dark_mode else "#C7C7CC"
        handle_pressed = "#8E8E90" if is_dark_mode else "#8E8E93"
        
        return f"""
            QScrollBar:vertical {{
                background-color: transparent;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {handle_color};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {handle_hover};
            }}
            
            QScrollBar::handle:vertical:pressed {{
                background-color: {handle_pressed};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: transparent;
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {handle_color};
                border-radius: 6px;
                min-width: 30px;
                margin: 2px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {handle_hover};
            }}
        """
