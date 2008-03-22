import os.path, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import appcfg, xmlres, viewmgr

class MainPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('MainPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_MAIN_PANEL")
        self.PostCreate(pre)

        # TODO: Implement some kind of demo functionality with the signals
        self.SetBackgroundColour(wx.WHITE)

