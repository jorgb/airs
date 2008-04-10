#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os

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
        dbfile = os.path.join(wx.StandardPaths.Get().GetUserDataDir(), 'series.db')
        if db.init(dbfile, False) == db.UPGRADE_NEEDED:
            res = wx.MessageBox("The database needs upgrading. Please backup the file:\n" + \
                                dbfile + "\n" + "And press YES to upgrade, NO to close the application",
                                "Warning", wx.ICON_WARNING | wx.YES_NO)
            if res == wx.YES:
                db.init(dbfile, True)               
            else:
                return 0

        MainFrame = AirsFrame(None, -1, appcfg.APP_TITLE)
        self.SetTopWindow(MainFrame)
        MainFrame.Show()
        return 1


    def OnExit(self):
        """
        Exit the application
        """
        appcfg.Write()

