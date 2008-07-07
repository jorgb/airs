import os
import platform

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

        self._layout = xrc.XRCCTRL(self, "ID_LAYOUT")
        self._layout.Append("Mobile (bare text)", appcfg.LAYOUT_MOBILE)
        self._layout.Append("Screen (small fonts and icons)", appcfg.LAYOUT_SCREEN)
        self._layout.Append("TV (big fonts and icons)", appcfg.LAYOUT_TV)

        layout = appcfg.options[appcfg.CFG_LAYOUT_SCREEN]
        for idx in xrange(0, self._layout.GetCount()):
            if self._layout.GetClientData(idx) == layout:
                self._layout.SetSelection(idx)
                break

        self._playerPath = xrc.XRCCTRL(self, "ID_PLAYER_PATH")
        self._playerArgs = xrc.XRCCTRL(self, "ID_PLAYER_ARGS")
        self._playerBtn = xrc.XRCCTRL(self, "ID_PLAYER_BROWSE")

        self._seriesPath = xrc.XRCCTRL(self, "ID_SERIES_ROOT")
        self._seriesBtn = xrc.XRCCTRL(self, "ID_SERIES_BROWSE")

        self._playerPath.SetValue(appcfg.options[appcfg.CFG_PLAYER_PATH])
        self._playerArgs.SetValue(appcfg.options[appcfg.CFG_PLAYER_ARGS])
        self._seriesPath.SetValue(appcfg.options[appcfg.CFG_SERIES_PATH])

        self.Bind(wx.EVT_BUTTON, self.__OnOK,  xrc.XRCCTRL(self, "wxID_OK"))
        self.Bind(wx.EVT_BUTTON, self._browseSeries, self._seriesBtn)
        self.Bind(wx.EVT_BUTTON, self._browsePlayer, self._playerBtn)


    def _browsePlayer(self, event):
        if platform.system().lower() == "windows":
            wildcard = "*.*"
        else:
            wildcard = "*"

        dlg = wx.FileDialog(self, "Select the player executable", os.path.dirname(self._playerPath.GetValue()),
                            "", wildcard, wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self._playerPath.SetValue(dlg.GetPath())


    def _browseSeries(self, event):
        dlg = wx.DirDialog(self, "Select path for series", self._seriesPath.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self._seriesPath.SetValue(dlg.GetPath())


    # --------------------------------------------------------------------------
    def __OnOK(self, event):
        """ Press OK, verify the path and notify if the path is not valid """

        appcfg.options[appcfg.CFG_LAYOUT_SCREEN] = self._layout.GetClientData(self._layout.GetSelection())
        appcfg.options[appcfg.CFG_PLAYER_PATH] = self._playerPath.GetValue()
        appcfg.options[appcfg.CFG_SERIES_PATH] = self._seriesPath.GetValue()
        appcfg.options[appcfg.CFG_PLAYER_ARGS] = self._playerArgs.GetValue()
        appcfg.Write()

        event.Skip()
