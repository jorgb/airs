import os, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import xmlres
from data import appcfg

class ViewSelectPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('ViewSelectPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_VIEWSELECTPANEL")
        self.PostCreate(pre)
        
        # TODO: Implement some kind of demo functionality with the signals
        self.SetBackgroundColour(wx.WHITE)
