#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import wx
import wx.xrc as xrc
import xmlres
from data import appcfg
from data import viewmgr, db, series_list

class SeriesDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("SeriesDlg.xrc")
        res.LoadOnDialog(pre, parent, "SeriesDlg")
        self.PostCreate(pre)
        
        self._editing = False
        
        self.Bind(wx.EVT_BUTTON, self._onOK,  xrc.XRCCTRL(self, "wxID_OK"))
        self._series_id = xrc.XRCCTRL(self, "ID_SERIES_ID")
        self._series_link = xrc.XRCCTRL(self, "ID_SERIES_LINK")
        

    # --------------------------------------------------------------------------
    def _onOK(self, event): 
        """ Press OK, verify the path and notify if the path is not valid """
        
        series_name = self._series_id.GetValue().strip()
        series_link = self._series_link.GetValue().strip()
        if not series_link or not series_name:
            wx.MessageBox("Please enter a valid URL or series name", "Error", wx.ICON_ERROR)
            return

        if not self._editing:
            # check for existence in database
            if db.store.find(series_list.Series, 
                             series_list.Series.name == unicode(series_name)).one():
                wx.MessageBox("A series with this name already exists", "Error", wx.ICON_ERROR)
                return

        event.Skip()


    def guiToObject(self, series):
        """
        Store all the GUI data in the series object
        """
        series_name = self._series_id.GetValue().strip()
        series_link = self._series_link.GetValue().strip()
        
        series.name = unicode(series_name)
        series.url = unicode(series_link)
        

    def objectToGui(self, series):
        """
        Store all the data of the series in the GUI
        """
        
        self._series_id.SetValue(series.name)
        self._series_link.SetValue(series.url)
        
        