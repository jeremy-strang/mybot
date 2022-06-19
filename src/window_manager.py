import win32gui, win32con, win32com.client
import re

class WindowManager:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self.handle = None
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self.handle = win32gui.FindWindow(class_name, window_name)
        return self.handle

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self.handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self.handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        if self.handle is None:
            self.find_d2r()
        if self.handle is not None:
            win32gui.BringWindowToTop(self.handle)
            self.shell.SendKeys("^")
            win32gui.SetForegroundWindow(self.handle)
            return True
        return False
    
    def find_d2r(self):
        self.find_window_wildcard("Diablo II: Resurrected")
        return self.handle is not None
