#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import sys
import wx
import wx.xrc as xrc
import xmlres
from data import appcfg, options
from data import viewmgr, db, searches

class EpisodeEditDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("EpisodeEditDlg.xrc")
        res.LoadOnDialog(pre, parent, "EpisodeEditDlg")
        self.PostCreate(pre)
                
        self.Bind(wx.EVT_BUTTON, self._onOK,  xrc.XRCCTRL(self, "wxID_OK"))

        
    def _onOK(self, event): 
        # TODO: Check for valid fields
        event.Skip()

