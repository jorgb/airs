#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os
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
        self._postponed = xrc.XRCCTRL(self, "ID_CANCELLED")
        self._update_period = xrc.XRCCTRL(self, "ID_UPDATE_PERIOD")
        self._period_select = xrc.XRCCTRL(self, "ID_PERIOD_SELECT")
        self._last_updated = xrc.XRCCTRL(self, "ID_UPDATE_DATE")
        self._seriesFolder = xrc.XRCCTRL(self, "ID_SERIES_PATH")
        self._seriesBrowse = xrc.XRCCTRL(self, "ID_SERIES_BROWSE")
        self._warning = xrc.XRCCTRL(self, "ID_WARNING")
        
        self._warning.Show(appcfg.options[appcfg.CFG_SERIES_PATH] == '')
        
        i = -1
        while i >= series_list.min_period:
            self._period_select.Append(series_list.period_trans[i], i)
            i -= 1
        self._period_select.Append(series_list.period_custom[1], 
                                   series_list.period_custom[0])
        
        self.Bind(wx.EVT_UPDATE_UI, self._onUpdateUI)
        self.Bind(wx.EVT_CHOICE, self._onPeriodSelect, self._period_select)
        self.Bind(wx.EVT_BUTTON, self._onSeriesBrowse, self._seriesBrowse)
    
    
    def _onSeriesBrowse(self, event):
        joined = False
        rootfolder = appcfg.options[appcfg.CFG_SERIES_PATH]
        seriesfolder = self._seriesFolder.GetValue()
        if not os.path.isabs(seriesfolder) and rootfolder != '':
            seriesfolder = os.path.join(rootfolder, seriesfolder)
            joined = True
                    
        dlg = wx.DirDialog(self, "Select the series path", seriesfolder)
        if dlg.ShowModal() == wx.ID_OK:
            if not joined:
                self._seriesFolder.SetValue(dlg.GetPath())
            else:
                cmnstr = os.path.commonprefix([rootfolder, dlg.GetPath()])
                if len(cmnstr) > 0:
                    self._seriesFolder.SetValue(dlg.GetPath()[len(cmnstr):].strip('/\\'))
                else:
                    self._seriesFolder.SetValue(dlg.GetPath())
        
    def _onPeriodSelect(self, event):
        lst = self._period_select
        if lst.GetClientData(lst.GetSelection()) == series_list.period_custom[0]:
            self._update_period.SetValue('0')
        else:
            self._update_period.SetValue('')
        

    def _onUpdateUI(self, event):
        lst = self._period_select
        idx = lst.GetSelection()
        if idx != wx.NOT_FOUND:
            # custom select enables edit box
            if lst.GetClientData(idx) == series_list.period_custom[0]:
                self._update_period.Enable(True)
            else:
                self._update_period.Enable(False)
                

    def _onOK(self, event): 
        """ Press OK, verify the path and notify if the path is not valid """
        
        series_name = self._series_id.GetValue().strip()
        series_link = self._series_link.GetValue().strip()
        if not series_name:
            wx.MessageBox("Please enter a valid series name", "Error", wx.ICON_ERROR)
            return

        if not self._editing:
            # check for existence in database
            if db.store.find(series_list.Series, 
                             series_list.Series.name == unicode(series_name)).one():
                wx.MessageBox("A series with this name already exists", "Error", wx.ICON_ERROR)
                return

        try:
            lst = self._period_select
            if lst.GetClientData(lst.GetSelection()) != series_list.period_custom[0]:
                upd = lst.GetClientData(lst.GetSelection())
            else:
                upd = int(self._update_period.GetValue())
        except ValueError:
            wx.MessageBox("Please enter a valid update period", "Error", wx.ICON_ERROR)
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
        
        series.folder = unicode(self._seriesFolder.GetValue())
        
        if self._postponed.GetValue():
            series.postponed = 1
        else:
            series.postponed = 0
            
        try:
            lst = self._period_select
            idx = lst.GetSelection()
            if lst.GetClientData(idx) == series_list.period_custom[0]:
                upd = int(self._update_period.GetValue())
            else:
                upd = lst.GetClientData(idx)
            series.update_period = upd
        except ValueError:
            pass
        

    def objectToGui(self, series):
        """
        Store all the data of the series in the GUI
        """
        
        self._series_id.SetValue(series.name)
        self._series_link.SetValue(series.url)
        self._postponed.SetValue(series.postponed != 0)

        per = series.update_period
        lst = self._period_select
        if per < 0:
            cdata = per
        else:
            cdata = series_list.period_custom[0]
            
        for i in xrange(0, lst.GetCount()):
            if lst.GetClientData(i) == cdata:
                lst.SetSelection(i)
                break
        if per >= 0:
            self._update_period.SetValue(str(per))
        else:
            self._update_period.SetValue('')
            
        self._seriesFolder.SetValue(series.folder)
            
