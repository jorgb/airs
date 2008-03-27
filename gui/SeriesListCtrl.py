import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin

class SeriesListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)


    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)


    def OnCheckItem(self, index, flag):
        pass
        