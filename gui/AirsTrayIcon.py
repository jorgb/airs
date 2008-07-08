import wx
import wx.lib.newevent
from data import appcfg, viewmgr
from images import icon_main
import menuhelper

class AirsTrayIcon(wx.TaskBarIcon):

    def __init__(self, parent):
        wx.TaskBarIcon.__init__(self)

        self._parent = parent

        self.SetIcon(self.makeIcon(icon_main.getImage()), appcfg.APP_TITLE)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self._onGuiTaskBarActivate)


    def CreatePopupMenu(self):
        """ Creates a popupmenu """
        popmenu = [ "browser", "update_all", "-", "restore_wnd", "exit"]

        traymenu = wx.Menu()
        menu_data = menuhelper.populate(traymenu, popmenu)

        id = menu_data["restore_wnd"].id
        traymenu.Enable(id, not self._parent.IsShown())
        self.Bind(wx.EVT_MENU, self._onRestoreWindow, id = id)

        id = menu_data["update_all"].id
        traymenu.Enable(id, not viewmgr.is_busy())
        self.Bind(wx.EVT_MENU, self._onUpdateAll, id = id)

        self.Bind(wx.EVT_MENU, self._onBrowserStart, id = menu_data["browser"].id)
        self.Bind(wx.EVT_MENU, self._onExit, id = menu_data["exit"].id)

        return traymenu

    def _onRestoreWindow(self, event):
        wx.CallAfter(self._parent._onGuiRestore, event)

    def _onBrowserStart(self, event):
        wx.CallAfter(self._parent._onStartBrowser, event)

    def _onUpdateAll(self, event):
        wx.CallAfter(self._parent._onUpdateAll, event)

    def _onExit(self, event):
        wx.CallAfter(self._parent._onGuiExit, event)

    def makeIcon(self, img):
        """ The various platforms have different requirements for the
            icon size... """
        #if "wxMSW" in wx.PlatformInfo:
        #    img = img.Scale(16, 16)
        #elif "wxGTK" in wx.PlatformInfo:
        #    img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        return wx.IconFromBitmap(img.ConvertToBitmap())


    def _onGuiTaskBarActivate(self, event):
        """ Icon is doubleclicked, so we need to take action """
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, -1)
        self._parent._onGuiRestore(evt)
