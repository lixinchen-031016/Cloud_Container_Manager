"""
系统主题检测器
自动检测 macOS 系统的深色/浅色模式
"""
import platform


class SystemThemeDetector:
    """
    系统主题检测器
    
    支持 macOS 系统主题检测，提供降级方案
    """
    
    _instance = None
    _current_theme = 'light'  # 默认浅色
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._is_macos = platform.system() == 'Darwin'
        self._pyobjc_available = False
        
        # 尝试导入 pyobjc
        if self._is_macos:
            try:
                from AppKit import NSAppearance
                self._pyobjc_available = True
                print("[ThemeDetector] PyObjC 可用，使用原生 API 检测主题")
            except ImportError:
                print("[ThemeDetector] PyObjC 不可用，使用降级方案")
        
        self._listeners = []
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'SystemThemeDetector':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_dark_mode(self) -> bool:
        """
        检测是否为深色模式
        
        Returns:
            是否为深色模式
        """
        if not self._is_macos:
            return False
        
        if self._pyobjc_available:
            try:
                from AppKit import NSAppearance, NSAppearanceNameDarkAqua
                appearance = NSAppearance.currentAppearance()
                # PyObjC 12+ 使用新的 API
                name = appearance.name
                is_dark = str(NSAppearanceNameDarkAqua) in str(name)
                self._current_theme = 'dark' if is_dark else 'light'
                return is_dark
            except Exception as e:
                print(f"[ThemeDetector] 检测失败：{e}")
                return self._current_theme == 'dark'
        else:
            # 降级方案：返回缓存值
            return self._current_theme == 'dark'
    
    def start_listening(self, callback) -> None:
        """
        开始监听主题变化
        
        Args:
            callback: 主题变化回调函数，参数为 is_dark_mode (bool)
        """
        self._listeners.append(callback)
        
        if self._is_macos and self._pyobjc_available:
            try:
                from AppKit import NSWorkspace
                from Foundation import NSNotificationCenter
                import objc
                
                center = NSNotificationCenter.defaultCenter()
                # PyObjC 12+ 需要使用 objc.selector 包装方法
                selector = objc.selector(self._on_theme_changed, signature=b'v@:@')
                center.addObserver_selector_name_object_(
                    self,
                    selector,
                    'NSWorkspaceAppearanceModeChangedNotification',
                    None
                )
                print("[ThemeDetector] 已注册主题变化监听")
            except Exception as e:
                print(f"[ThemeDetector] 注册监听失败：{e}")
    
    def _on_theme_changed(self, notification) -> None:
        """主题变化通知处理"""
        try:
            is_dark = self.is_dark_mode()
            print(f"[ThemeDetector] 主题已切换：{'深色' if is_dark else '浅色'}")
            
            # 通知所有监听器
            for callback in self._listeners:
                try:
                    callback(is_dark)
                except Exception as e:
                    print(f"[ThemeDetector] 通知回调失败：{e}")
        except Exception as e:
            print(f"[ThemeDetector] 处理主题变化失败：{e}")
    
    def stop_listening(self) -> None:
        """停止监听主题变化"""
        if self._is_macos and self._pyobjc_available:
            try:
                from Foundation import NSNotificationCenter
                
                center = NSNotificationCenter.defaultCenter()
                center.removeObserver(self)
                print("[ThemeDetector] 已停止主题变化监听")
            except Exception as e:
                print(f"[ThemeDetector] 停止监听失败：{e}")
        
        self._listeners.clear()
    
    def force_set_theme(self, theme: str) -> None:
        """
        强制设置主题（用于测试或手动切换）
        
        Args:
            theme: 'light' 或 'dark'
        """
        if theme not in ['light', 'dark']:
            raise ValueError("theme 必须是 'light' 或 'dark'")
        
        old_theme = self._current_theme
        self._current_theme = theme
        
        # 如果主题改变，通知监听器
        if old_theme != theme:
            is_dark = theme == 'dark'
            for callback in self._listeners:
                try:
                    callback(is_dark)
                except Exception as e:
                    print(f"[ThemeDetector] 通知回调失败：{e}")
