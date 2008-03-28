import wx
from data import appcfg

ID_TRAYICON_RESTORE = wx.NewId()
ID_TRAYICON_CLOSE   = wx.NewId()

from images import icon_main
from data import viewmgr

class AirsTrayIcon(wx.TaskBarIcon):
    
    def __init__(self):
        wx.TaskBarIcon.__init__(self)

        # set the image
        self.SetIcon(self.makeIcon(icon_main.getImage()), appcfg.APP_TITLE)
        
        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self._onGuiTaskBarActivate)
        self.Bind(wx.EVT_MENU, self._onGuiTaskBarActivate, id = ID_TRAYICON_RESTORE)
        self.Bind(wx.EVT_MENU, self._onGuiTaskBarClose, id = ID_TRAYICON_CLOSE)


    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default event_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(ID_TRAYICON_RESTORE, "Restore ...")
        menu.AppendSeparator()
        menu.Append(ID_TRAYICON_CLOSE,   "Exit")
        return menu


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
    

    def _onGuiTaskBarActivate(self, eveznt):
        """
        Icon is doubleclicked, so we need to take action
        """
        viewmgr.app_restore()


    def _onGuiTaskBarClose(self, event):
        """
        Signal close to the view manager so we can close the main application
        """
        viewmgr.app_close()
