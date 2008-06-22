import os

import wx
import wx.xrc as xrc
import xmlres
from data import appcfg

class OptionsDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("OptionsDlg.xrc")
        res.LoadOnDialog(pre, parent, "OptionsDialog")
        self.PostCreate(pre)
       
        #self.Bind(wx.EVT_BUTTON, self.__OnOK,  xrc.XRCCTRL(self, "wxID_OK"))

        # TODO: Set the settings in the dialog controls

    # --------------------------------------------------------------------------
    def __OnOK(self, event): 
        """ Press OK, verify the path and notify if the path is not valid """
        
        # TODO: Verify the controls and put them in the appcfg.options dictionary
        
        # TODO: return from this function without event.Skip if not correct        

        event.Skip()


