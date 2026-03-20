"""
macOS 菜单栏服务
在系统菜单栏添加快捷操作和状态显示
"""
import platform
from typing import Optional, List, Dict, Any


class MenuBarService:
    """
    macOS 菜单栏服务
    
    功能：
    - 在系统菜单栏显示应用图标
    - 快速访问菜单（连接服务器、查看状态）
    - 显示通知计数
    - 支持深色模式
    """
    
    _instance: Optional['MenuBarService'] = None
    
    def __new__(cls) -> 'MenuBarService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._is_macos = platform.system() == 'Darwin'
        self._pyobjc_available = False
        self._status_item = None
        self._menu = None
        self._servers: List[Dict[str, Any]] = []
        self._notification_count = 0
        
        # 尝试导入 PyObjC
        if self._is_macos:
            try:
                from AppKit import NSStatusItem, NSMenu, NSImage, NSStatusBar
                from Foundation import NSRunLoop, NSDate, NSTimer
                self._pyobjc_available = True
                print("[MenuBarService] PyObjC AppKit 可用")
            except ImportError:
                print("[MenuBarService] PyObjC AppKit 不可用，使用降级方案")
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'MenuBarService':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self) -> None:
        """初始化菜单栏"""
        if not self._is_macos or not self._pyobjc_available:
            print("[MenuBarService] 无法创建原生菜单栏")
            return
        
        try:
            from AppKit import NSStatusBar, NSStatusItem, NSMenu, NSImage
            import objc
            
            # 创建状态栏项目
            status_bar = NSStatusBar.systemStatusBar()
            self._status_item = status_bar.statusItemWithLength_(-1.0)  # 可变长度
            
            # 设置标题或图标
            self._status_item.setTitle_("☁️ CCM")
            
            # 创建菜单
            self._menu = NSMenu.alloc().init()
            self._update_menu()
            
            # 设置菜单
            self._status_item.setMenu_(self._menu)
            
            print("[MenuBarService] 菜单栏已创建")
        except Exception as e:
            print(f"[MenuBarService] 创建菜单栏失败：{e}")
    
    def _update_menu(self) -> None:
        """更新菜单内容"""
        if not self._menu:
            return
        
        try:
            from AppKit import NSMenuItem
            import objc
            
            # 清空菜单
            self._menu.removeAllItems()
            
            # 添加服务器列表
            if self._servers:
                for server in self._servers[:5]:  # 最多显示 5 个
                    server_name = server.get('name', server.get('hostname', '未知'))
                    status = "● 在线" if server.get('connected', False) else "○ 离线"
                    
                    item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                        f"{server_name} ({status})", None, ""
                    )
                    item.setEnabled_(False)  # 暂时禁用
                    self._menu.addItem_(item)
                
                self._menu.addItem_(NSMenuItem.separatorItem())
            
            # 添加操作菜单（暂时禁用，因为没有实现对应的方法）
            connect_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "快速连接...", None, ""
            )
            connect_item.setEnabled_(False)
            self._menu.addItem_(connect_item)
            
            show_app_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "打开应用", None, ""
            )
            show_app_item.setEnabled_(False)
            self._menu.addItem_(show_app_item)
            
            self._menu.addItem_(NSMenuItem.separatorItem())
            
            # 退出
            quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "退出", None, "q"
            )
            self._menu.addItem_(quit_item)
            
        except Exception as e:
            print(f"[MenuBarService] 更新菜单失败：{e}")
    
    def update_servers(self, servers: List[Dict[str, Any]]) -> None:
        """
        更新服务器列表
        
        Args:
            servers: 服务器信息列表
        """
        self._servers = servers
        if self._menu:
            self._update_menu()
    
    def set_notification_count(self, count: int) -> None:
        """
        设置通知计数
        
        Args:
            count: 通知数量
        """
        self._notification_count = count
        
        # 更新标题显示通知数
        if self._status_item and count > 0:
            self._status_item.setTitle_(f"☁️ {count}")
        elif self._status_item:
            self._status_item.setTitle_("☁️ CCM")
    
    def quick_connect(self) -> None:
        """快速连接（回调方法）"""
        print("[MenuBarService] 快速连接...")
        # TODO: 实现快速连接逻辑
    
    def show_application(self) -> None:
        """显示应用窗口（回调方法）"""
        print("[MenuBarService] 显示应用窗口")
        # TODO: 实现显示窗口逻辑
    
    def quit_application(self) -> None:
        """退出应用（回调方法）"""
        print("[MenuBarService] 退出应用")
        # TODO: 实现退出逻辑
    
    def cleanup(self) -> None:
        """清理资源"""
        if self._status_item:
            from AppKit import NSStatusBar
            status_bar = NSStatusBar.systemStatusBar()
            status_bar.removeStatusItem_(self._status_item)
            self._status_item = None
        
        print("[MenuBarService] 已清理")


# 全局菜单栏服务实例
_global_menu_bar_service: Optional[MenuBarService] = None


def get_menu_bar_service() -> MenuBarService:
    """获取全局菜单栏服务实例"""
    global _global_menu_bar_service
    if _global_menu_bar_service is None:
        _global_menu_bar_service = MenuBarService.get_instance()
    return _global_menu_bar_service
