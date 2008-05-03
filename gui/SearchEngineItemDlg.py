#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import wx
import wx.xrc as xrc
import xmlres
from data import appcfg
from data import viewmgr, db, searches

class SearchEngineItemDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("SearchEngineItemDlg.xrc")
        res.LoadOnDialog(pre, parent, "SearchEngineItemDlg")
        self.PostCreate(pre)
        
        self.Bind(wx.EVT_BUTTON, self._onOK,  xrc.XRCCTRL(self, "wxID_OK"))
                    
        self._name = xrc.XRCCTRL(self, "ID_NAME")
        self._url = xrc.XRCCTRL(self, "ID_URL")
        
        
    def _onOK(self, event): 
        """ Press OK, verify the path and notify if the path is not valid """
        
        if self._name.GetValue().strip() == '':
            wx.MessageBox("Enter a valid name", "Error", wx.ICON_ERROR)
            return
        
        url = self._url.GetValue().strip()
        if not url.startswith("http"):
            wx.MessageBox("Enter a valid URL", "Error", wx.ICON_ERROR)
            return
        
        event.Skip()


    def guiToObject(self, engine):
        """
        Store all the GUI data in the series object
        """
        engine.name = unicode(self._name.GetValue().strip())
        engine.url = unicode(self._url.GetValue().strip())
        
        
    def objectToGui(self, engine):
        """
        Store all the data of the series in the GUI
        """
        self._name.SetValue(engine.name)
        self._url.SetValue(engine.url)
