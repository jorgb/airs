import wx
import wx.lib.newevent
from data import appcfg
from images import icon_main

SHOW_MENU       = 0
ACTIVATE_WINDOW = 1

class AirsTrayIcon(wx.TaskBarIcon):
    
    def __init__(self, parent):
        wx.TaskBarIcon.__init__(self)
        
        self._parent = parent

        self.SetIcon(self.makeIcon(icon_main.getImage()), appcfg.APP_TITLE)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self._onGuiTaskBarActivate)


    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default event_RIGHT_DOWN event. The menu creation
        is delegated to the main frame window for ease of handling
        """
        self._parent._callbackTrayIcon(SHOW_MENU)


    def makeIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        return wx.IconFromBitmap(img.ConvertToBitmap())
    

    def _onGuiTaskBarActivate(self, event):
        """
        Icon is doubleclicked, so we need to take action
        """
        self._parent._callbackTrayIcon(ACTIVATE_WINDOW)

