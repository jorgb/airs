#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os
from optparse import OptionParser

import wx
import xmlres
from data import appcfg, db
from AirsFrame import AirsFrame

class AirsApp(wx.App):

    def OnInit(self):
        """
        Initialize and show application
        """

        wx.InitAllImageHandlers()

        self.SetAppName(appcfg.APP_NAME)

        appcfg.Read()
                
        # initialize / create database
        if not os.path.exists(wx.StandardPaths.Get().GetUserDataDir()):
            os.makedirs(wx.StandardPaths.Get().GetUserDataDir())
        
        if not appcfg.dbpath:
            appcfg.dbpath = os.path.join(wx.StandardPaths.Get().GetUserDataDir(), appcfg.DB_NAME)
            
        if db.init(appcfg.dbpath, False) == db.UPGRADE_NEEDED:
            res = wx.MessageBox("The database needs upgrading. Please backup the file:\n" + \
                                appcfg.dbpath + "\n" + "And press YES to upgrade, NO to close the application",
                                "Warning", wx.ICON_WARNING | wx.YES_NO)
            if res == wx.YES:
                if db.init(appcfg.dbpath, True) == db.UPGRADE_FAILED:
                    wx.MessageBox("Somehow the upgrade failed. Contact me for help!", "Error" , wx.ICON_HAND)
                    return 0
            else:
                return 0

        self._frame = AirsFrame(None, -1, appcfg.APP_TITLE)
        self.SetTopWindow(self._frame)
        self._frame.Show(not appcfg.options[appcfg.CFG_TRAY_MINIMIZE])
        return 1


    def OnExit(self):
        """
        Exit the application
        """
        db._close()
        appcfg.Write()

