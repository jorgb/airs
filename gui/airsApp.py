import os

import wx
import appcfg, xmlres
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
        MainFrame.Show(not appcfg.options[appcfg.CFG_LAYOUT_HIDDEN])
        return 1


    def OnExit(self):
        """
        Exit the application
        """
        appcfg.Write()

