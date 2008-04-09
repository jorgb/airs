#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os

import wx
import xmlres
from data import appcfg
from AirsFrame import AirsFrame

class AirsApp(wx.App):

    def OnInit(self):
        """
        Initialize and show application
        """

        wx.InitAllImageHandlers()

        self.SetAppName(appcfg.APP_NAME)

        appcfg.Read()

        MainFrame = AirsFrame(None, -1, appcfg.APP_TITLE)
        self.SetTopWindow(MainFrame)
        MainFrame.Show()
        return 1


    def OnExit(self):
        """
        Exit the application
        """
        appcfg.Write()

