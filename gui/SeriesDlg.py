import wx
import wx.xrc as xrc
import xmlres
from data import appcfg
from data import viewmgr

class SeriesDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("SeriesDlg.xrc")
        res.LoadOnDialog(pre, parent, "SeriesDlg")
        self.PostCreate(pre)
        self._editing = False
        
        self.Bind(wx.EVT_BUTTON, self.__onOK,  xrc.XRCCTRL(self, "wxID_OK"))
        self._series_id = xrc.XRCCTRL(self, "ID_SERIES_ID")
        self._series_link = xrc.XRCCTRL(self, "ID_SERIES_LINK")
        

    # --------------------------------------------------------------------------
    def __onOK(self, event): 
        """ Press OK, verify the path and notify if the path is not valid """
        
        series_id = self._series_id.GetValue().strip()
        series_link = self._series_link.GetValue().strip()
        if not series_link or not series_id:
            wx.MessageBox("Please enter a valid URL or series ID", "Error", wx.ICON_ERROR)
            return

        if not self._editing:
            if series_id.lower() in viewmgr._series_list._series:
                wx.MessageBox("A series with this ID already exists", "Error", wx.ICON_ERROR)
                return

        event.Skip()


    def guiToObject(self, series):
        """
        Store all the GUI data in the series object
        """
        series_id = self._series_id.GetValue().strip()
        series_link = self._series_link.GetValue().strip()
        
        series._serie_name = series_id
        series._link = series_link
        

    def objectToGui(self, series):
        """
        Store all the data of the series in the GUI
        """
        
        self._series_id.SetValue(series._serie_name)
        series_link = self._series_link.SetValue(series._link)
