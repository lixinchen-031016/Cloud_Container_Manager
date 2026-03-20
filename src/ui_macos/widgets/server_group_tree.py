"""
macOS 风格服务器分组树形视图
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QMenu, QAction, QDialog, QLineEdit, QColorDialog, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from typing import Optional, List
from services.server_group_service import ServerGroup, ManagedServer, get_server_group_service
from ui_macos.widgets.themed_widget import ThemedWidget


class ServerGroupTree(ThemedWidget):
    """
    macOS 风格服务器分组树形视图
    
    功能：
    - 显示分组和服务器层级结构
    - 支持右键菜单操作
    - 拖拽排序（待实现）
    - 支持深色模式
    """
    
    # 信号
    server_selected = pyqtSignal(object)  # 服务器被选中
    group_selected = pyqtSignal(str)      # 分组被选中
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.group_service = get_server_group_service()
        
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("📁 服务器分组")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {self.get_text_color()};
            padding: 15px 15px 10px 15px;
        """)
        layout.addWidget(title_label)
        
        # 树形视图
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        # 设置样式
        self._apply_tree_theme()
        
        layout.addWidget(self.tree)
        self.setLayout(layout)
    
    def _apply_tree_theme(self):
        """应用主题到树形视图"""
        bg_color = self.get_background_color()
        text_color = self.get_text_color()
        selected_bg = "rgba(10, 132, 255, 0.2)" if self._is_dark_mode else "#E8F2FF"
        selected_text = self.get_accent_color()
        hover_bg = "#3A3A3C" if self._is_dark_mode else "#F5F5F7"
        
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                outline: none;
            }}
            
            QTreeWidget::item {{
                padding: 8px 10px;
                border-radius: 6px;
            }}
            
            QTreeWidget::item:hover {{
                background-color: {hover_bg};
            }}
            
            QTreeWidget::item:selected {{
                background-color: {selected_bg};
                color: {selected_text};
            }}
        """)
    
    def _load_data(self):
        """加载数据"""
        self.tree.clear()
        
        # 添加未分组节点
        ungrouped_item = QTreeWidgetItem(self.tree)
        ungrouped_item.setText(0, "📄 未分组")
        ungrouped_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'ungrouped'})
        
        # 加载未分组的服务器
        ungrouped_servers = self.group_service.get_ungrouped_servers()
        for server in ungrouped_servers:
            server_item = QTreeWidgetItem(ungrouped_item)
            server_item.setText(0, f"🖥️ {server.name}")
            server_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'server',
                'server': server
            })
        
        # 加载所有分组
        groups = self.group_service.get_groups()
        for group in groups:
            group_item = QTreeWidgetItem(self.tree)
            group_item.setText(0, f"📁 {group.name} ({len(group.server_ids)})")
            group_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'group',
                'group': group
            })
            
            # 设置分组颜色
            group_item.setForeground(0, QColor(group.color))
            
            # 加载分组中的服务器
            servers = self.group_service.get_servers_in_group(group.id)
            for server in servers:
                server_item = QTreeWidgetItem(group_item)
                server_item.setText(0, f"🖥️ {server.name}")
                server_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'server',
                    'server': server
                })
        
        # 展开所有节点
        self.tree.expandAll()
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.tree.itemAt(pos)
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        menu = QMenu(self)
        item_type = data.get('type')
        
        if item_type == 'group':
            # 分组菜单
            expand_action = QAction("展开/折叠", self)
            expand_action.triggered.connect(lambda: self._toggle_group(item))
            menu.addAction(expand_action)
            
            rename_action = QAction("重命名", self)
            rename_action.triggered.connect(lambda: self._rename_group(data['group']))
            menu.addAction(rename_action)
            
            color_action = QAction("更改颜色", self)
            color_action.triggered.connect(lambda: self._change_group_color(data['group']))
            menu.addAction(color_action)
            
            menu.addSeparator()
            
            delete_action = QAction("删除分组", self)
            delete_action.triggered.connect(lambda: self._delete_group(data['group']))
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            add_server_action = QAction("添加服务器到此分组", self)
            add_server_action.triggered.connect(lambda: self._add_server_to_group(data['group'].id))
            menu.addAction(add_server_action)
        
        elif item_type == 'server':
            # 服务器菜单
            connect_action = QAction("连接", self)
            connect_action.triggered.connect(lambda: self._connect_server(data['server']))
            menu.addAction(connect_action)
            
            menu.addSeparator()
            
            move_action = QAction("移动到分组", self)
            move_action.triggered.connect(lambda: self._move_server(data['server']))
            menu.addAction(move_action)
            
            edit_tags_action = QAction("编辑标签", self)
            edit_tags_action.triggered.connect(lambda: self._edit_tags(data['server']))
            menu.addAction(edit_tags_action)
            
            menu.addSeparator()
            
            remove_action = QAction("删除", self)
            remove_action.triggered.connect(lambda: self._remove_server(data['server']))
            menu.addAction(remove_action)
        
        elif item_type == 'ungrouped':
            # 未分组菜单
            add_server_action = QAction("添加服务器", self)
            add_server_action.triggered.connect(lambda: self._add_server_to_group(None))
            menu.addAction(add_server_action)
            
            menu.addSeparator()
            
            create_group_action = QAction("创建新分组", self)
            create_group_action.triggered.connect(lambda: self._create_group())
            menu.addAction(create_group_action)
        
        if menu.actions():
            menu.exec(self.tree.viewport().mapToGlobal(pos))
    
    def _on_item_clicked(self, item, column):
        """项目点击事件"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data.get('type') == 'group':
            self.group_selected.emit(data['group'].id)
        elif data.get('type') == 'server':
            self.server_selected.emit(data['server'])
    
    def _toggle_group(self, item):
        """切换分组展开/折叠"""
        if item.isExpanded():
            item.setExpanded(False)
        else:
            item.setExpanded(True)
    
    def _rename_group(self, group: ServerGroup):
        """重命名分组"""
        dialog = QDialog(self)
        dialog.setWindowTitle("重命名分组")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        input = QLineEdit(group.name)
        input.setPlaceholderText("分组名称")
        layout.addWidget(input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = input.text().strip()
            if new_name:
                self.group_service.update_group(group.id, name=new_name)
                self._load_data()
    
    def _change_group_color(self, group: ServerGroup):
        """更改分组颜色"""
        color = QColorDialog.getColor(QColor(group.color), self, "选择分组颜色")
        if color.isValid():
            self.group_service.update_group(group.id, color=color.name())
            self._load_data()
    
    def _delete_group(self, group: ServerGroup):
        """删除分组"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除分组 \"{group.name}\" 吗？\n\n该分组的服务器将移到未分组。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.group_service.delete_group(group.id)
            self._load_data()
    
    def _create_group(self):
        """创建新分组"""
        dialog = QDialog(self)
        dialog.setWindowTitle("创建新分组")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("分组名称:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("例如：生产环境")
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("分组颜色:"))
        color_btn = QPushButton("#007AFF")
        
        def select_color():
            color = QColorDialog.getColor(QColor("#007AFF"), self, "选择分组颜色")
            if color.isValid():
                color_btn.setText(color.name())
                color_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
        
        color_btn.clicked.connect(select_color)
        layout.addWidget(color_btn)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("创建")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text().strip()
            color = color_btn.text()
            if name:
                self.group_service.create_group(name, color)
                self._load_data()
    
    def _add_server_to_group(self, group_id: Optional[str]):
        """添加服务器到分组"""
        # TODO: 显示添加服务器对话框
        QMessageBox.information(self, "提示", "添加服务器功能待实现")
    
    def _move_server(self, server: ManagedServer):
        """移动服务器到另一个分组"""
        # TODO: 显示分组选择对话框
        QMessageBox.information(self, "提示", "移动服务器功能待实现")
    
    def _edit_tags(self, server: ManagedServer):
        """编辑服务器标签"""
        # TODO: 显示标签编辑对话框
        QMessageBox.information(self, "提示", "编辑标签功能待实现")
    
    def _remove_server(self, server: ManagedServer):
        """删除服务器"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除服务器 \"{server.name}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.group_service.remove_server_from_group(server.id)
            self._load_data()
    
    def _connect_server(self, server: ManagedServer):
        """连接服务器"""
        # TODO: 触发连接逻辑
        print(f"[ServerGroupTree] 连接服务器：{server.name} ({server.hostname})")
    
    def on_theme_changed(self, is_dark_mode: bool) -> None:
        """主题变化处理"""
        self._apply_tree_theme()
        self._load_data()
