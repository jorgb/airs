import os.path
import sys

import wx
from wx.lib.wordwrap import wordwrap
from wx.lib.pubsub import Publisher

from data import appcfg, viewmgr, signals

# gui elements
import MainPanel
import OptionsDlg
import AirsTrayIcon

# images
from images import icon_main, icon_about
from images import icon_home, icon_help, \
                   icon_visit_site
from images import icon_preferences 
from images import icon_add, icon_delete, icon_edit

class AirsFrame(wx.Frame):
    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._trayIcon = None                       
        
        self._connectSignals()

        # instantiate the GUI
        self._createMenu()
        self._createWindows()
        self._createTrayIcon()
        self._createStatusBar()

        # generic application events
        self.Bind(wx.EVT_CLOSE, self._onGuiClose)
        self.Bind(wx.EVT_UPDATE_UI, self._onUpdateUI)
        self.Bind(wx.EVT_ICONIZE, self._onGuiIconize)

        # setup our application title and icon
        self.SetTitle(appcfg.APP_TITLE)
        self.SetIcon(wx.IconFromBitmap(icon_main.getBitmap()))

        # put windows like they were the last time
        self._restoreWindowLayout()
                
        # init viewmgr (always do this last so that
        # signals to be emitted can access controls)
        viewmgr.app_init()
        
        # periodic GUI update timer
        self.tmr = wx.Timer(self)
        self.tmr.Start(500)
        self.Bind(wx.EVT_TIMER, self._onTimer, self.tmr)
        
    # ========================== GUI CREATION CODE =============================

    def _createTrayIcon(self):
        """
        Creates the tray icon for this application
        """
        self._trayIcon = AirsTrayIcon.AirsTrayIcon()
    
    
    def _createMenu(self):
        """
        Creates the menu system for the application, and initializes the
        event handlers for it.
        """

        # create menu
        self._menuBar = wx.MenuBar()
        self.SetMenuBar(self._menuBar)

        # file menu
        filemnu = wx.Menu()
        
        self._menuExit = wx.MenuItem(filemnu, wx.NewId(), "E&xit", 
                                     "Exit the application", wx.ITEM_NORMAL)
        filemnu.AppendItem(self._menuExit)
        self._menuBar.Append(filemnu, "&File")

        # Series menu
        mnu = wx.Menu()
        self._menuAddNew = wx.MenuItem(mnu, wx.NewId(), "&Add ...\tCtrl+A", 
                                       "Add a new Series", wx.ITEM_NORMAL)
        self._menuAddNew.SetBitmap(icon_add.getBitmap())
        mnu.AppendItem(self._menuAddNew)

        self._menuEdit = wx.MenuItem(mnu, wx.NewId(), "&Edit ...\tCtrl+E", 
                                     "Edit Series properties", wx.ITEM_NORMAL)
        self._menuEdit.SetBitmap(icon_edit.getBitmap())
        mnu.AppendItem(self._menuEdit)

        self._menuDelete = wx.MenuItem(mnu, wx.NewId(), "&Delete\tCtrl+D", 
                                       "Delete this Series", wx.ITEM_NORMAL)
        self._menuDelete.SetBitmap(icon_delete.getBitmap())
        mnu.AppendItem(self._menuDelete)    
        self._menuBar.Append(mnu, "&Series")

        # tools menu
        mnu = wx.Menu()
        self._menuOptions = wx.MenuItem(mnu, wx.NewId(), "&Preferences ...", 
                                        "Open the application preferences", wx.ITEM_NORMAL)
        self._menuOptions.SetBitmap(icon_preferences.getBitmap())
        mnu.AppendItem(self._menuOptions)
        self._menuBar.Append(mnu, "&Tools")

        # window layout menu
        mnu = wx.Menu()                          
        self._menuTrayMinimize = wx.MenuItem(mnu, wx.NewId(), "Minimize to tray", 
                                             "Upon minimize, hide in system tray", wx.ITEM_CHECK)
        mnu.AppendItem(self._menuTrayMinimize)
        
        self._menuBar.Append(mnu, "&Window")
        
        # help menu
        mnu = wx.Menu()
        self._menuHelp = wx.MenuItem(mnu, wx.NewId(), "&Help ... ", 
                                     "Show the application help", wx.ITEM_NORMAL)
        self._menuHelp.SetBitmap(icon_help.getBitmap())
        mnu.AppendItem(self._menuHelp)

        self._menuHelpVisitSite = wx.MenuItem(mnu, wx.NewId(), "&Visit Site ... ", 
                                              "Visit the project site", wx.ITEM_NORMAL)
        self._menuHelpVisitSite.SetBitmap(icon_visit_site.getBitmap())
        mnu.AppendItem(self._menuHelpVisitSite)
        mnu.AppendSeparator()

        self._menuHelpAbout = wx.MenuItem(mnu, wx.NewId(), "&About ...", 
                                          "Show the about dialog", wx.ITEM_NORMAL)
        mnu.AppendItem(self._menuHelpAbout)
        self._menuBar.Append(mnu, "&Help")

        # recent file list, put this last in menu creation
        self._fileHistory = wx.FileHistory(appcfg.MAX_HISTORY_FILES, wx.ID_FILE1)
        self._fileHistory.UseMenu(filemnu)

        # initialize menu event handlers
        self.Bind(wx.EVT_MENU, self._onGuiAbout, self._menuHelpAbout)
        self.Bind(wx.EVT_MENU, self._onGuiShowOptions, self._menuOptions)
        self.Bind(wx.EVT_MENU, self._onGuiExit, self._menuExit)
        self.Bind(wx.EVT_MENU, self._onGuiVisitSite, self._menuHelpVisitSite)
        self.Bind(wx.EVT_MENU, self._onGuiMinimizeToTray, self._menuTrayMinimize)

        self.Bind(wx.EVT_MENU, self._onGuiAddNew, self._menuAddNew)
        self.Bind(wx.EVT_MENU, self._onGuiEdit, self._menuEdit)
        self.Bind(wx.EVT_MENU, self._onGuiDelete, self._menuDelete)
    
        
    def _createWindows(self):
        """
        Create the main window that this frame contains
        """
        # create main panel
        pnl = MainPanel.MainPanel(self)
        
    def _createStatusBar(self):
        """
        Creates a status bar on the current frame
        """
        # specify your statusbar here, add more fields if needed
        self._statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self._statusbar.SetStatusWidths([-1, -2])            
                
    
    # ======================== ITEM MANAGEMENT METHODS ========================= 
    
    def _onGuiAddNew(self, event):
        """ Event handler to add a new _cvl_ITEM_ """
        pass


    def _onGuiEdit(self, event):
        """ Event handler to edit a _cvl_ITEM_ """
        pass


    def _onGuiDelete(self, event):
        """ Event handler for deleting a _cvl_ITEM_ """
        pass
    

    # ============================= CLOSE METHODS ==============================
    
    def _onGuiExit(self, event):
        """ 
        Attempt to close the main window
        """
        viewmgr.app_close()


    def _onSignalClose(self, msg):
        """
        Last moment to save anything, let's do it here
        """
        self._saveWindowLayout()
        
        # TODO: Delete FileHistory object!!
        
        # save recent opened files
        self._fileHistory.Save(appcfg.Get())

        if viewmgr.is_closing:
            viewmgr.app_destroy()
            self.Close()


    def _onGuiClose(self, event):
        """
        We send the close event and veto if the user does not want to close
        """

        # send a signal to the view manager if someone 
        # closes the form by clicking the 'X' which is not
        # the normal way to close
        if not viewmgr.is_closing:
            if not viewmgr.app_close() and event.CanVeto():
                event.Veto()
                return

        if self._trayIcon is not None:
            self._trayIcon.Destroy()
            self._trayIcon = None
        
        event.Skip()            


    # ==================== LAYOUT AND UI UPDATE METHODS ========================
    
    def _onUpdateUI(self, event):
        """
        This event is called periodically to allow the user to update the
        menu / toolbar / buttons based upon the internal application state.
        """

        self._menuBar.Check(self._menuTrayMinimize.GetId(), 
                            appcfg.options[appcfg.CFG_TRAY_MINIMIZE])
        
        # TODO: Add your enable / disable control code here
        pass

        
    def _saveWindowLayout(self):
        """
        Saves the window layout for later use
        """
        # save windows layout
        width, height = self.GetSize()
        appcfg.options[appcfg.CFG_LAYOUT_HIDDEN] = not self.IsShown()

        # prevent invalid sizes to be stored, check for iconized app
        if not self.IsIconized():
            appcfg.options[appcfg.CFG_LAYOUT_LAST_H] = height
            appcfg.options[appcfg.CFG_LAYOUT_LAST_W] = width

            (xpos, ypos) = self.GetPosition()
            appcfg.options[appcfg.CFG_LAYOUT_LAST_X] = xpos
            appcfg.options[appcfg.CFG_LAYOUT_LAST_Y] = ypos
        

    def _restoreWindowLayout(self):
        """
        Restores the layout from the windows written in the settings
        """

        # retrieve height / width of main window
        width, height = appcfg.options[appcfg.CFG_LAYOUT_LAST_W], \
                        appcfg.options[appcfg.CFG_LAYOUT_LAST_H]
        xpos, ypos = appcfg.options[appcfg.CFG_LAYOUT_LAST_X], \
                     appcfg.options[appcfg.CFG_LAYOUT_LAST_Y]
        self.SetSize((width, height))
        self.SetPosition((xpos, ypos))
        

    def _onSignalAppRestore(self, msg):
        """
        Restore the window when this is iconized or made hidden
        """
        if self.IsIconized():
            self.Iconize(False)
        if not self.IsShown():
            self.Show(True)
            appcfg.options[appcfg.CFG_LAYOUT_HIDDEN] = False
        self.Raise()    


    def _onGuiIconize(self, event):
        """
        Iconize event. When a tray icon is present and the 'minimize to tray' 
        option is selected, the window is made hidden, which appears it is 
        minimized to the system tray
        """
        if event.Iconized() and appcfg.options[appcfg.CFG_TRAY_MINIMIZE] == True:
            self.Show(False)                   


    def _onGuiMinimizeToTray(self, event):
        """
        Event that sets or clears the minimize to tray option
        """
        opt = not appcfg.options[appcfg.CFG_TRAY_MINIMIZE]
        appcfg.options[appcfg.CFG_TRAY_MINIMIZE] = opt   


    def _onTimer(self, event):
        """
        Periodic check function to update various GUI elements.
        We could use OnGUIUpdate but it is sent too sporadically
        """
        series_title = viewmgr.get_current_title()        
        if series_title:
            self._statusbar.SetStatusText("Processing: %s" % series_title, 1)
        else:
            self._statusbar.SetStatusText("Idle ...", 1)
        pass
    
        
    # ============================ VARIOUS METHODS =============================

    def _connectSignals(self):
        """
        Connects all the signals used in this application to members of this
        main frame. The view manager sends out signals when functionality of
        your application is called
        """
        Publisher().subscribe(self._onSignalClose, signals.APP_CLOSE)
        Publisher().subscribe(self._onSignalAppRestore, signals.APP_RESTORE)
        Publisher().subscribe(self._onSignalSettingsChanged, signals.APP_SETTINGS_CHANGED)


    def _onGuiShowOptions(self, event):
        """ 
        Show the options dialog, all options saving is done inside the dialog
        itself so there is no need for catching the modalresult 
        """
        dlg = OptionsDlg.OptionsDlg(self)
        dlg.Center()
        if dlg.ShowModal() == wx.ID_OK:
            viewmgr.app_settings_changed()
        dlg.Destroy()


    def _onSignalSettingsChanged(self, msg):
        """
        Act upon a change of settings. In here you can update the GUI controls
        that need updating
        """
        # TODO: Implement to reflect changed settings
        print "TODO: Implement _onSignalSettingsChanged() to reflect changed settings"


    def _onGuiAbout(self, event):
        """ 
        Show the about dialog with information about the application 
        """

        info = wx.AboutDialogInfo()
        info.Icon = wx.IconFromBitmap(icon_about.getBitmap())
        info.Name = appcfg.APP_TITLE
        info.Version = "v%s" % appcfg.APP_VERSION
        if not appcfg.APP_VENDOR:
            info.Copyright = "(C) 2007 %s" % appcfg.APP_AUTHOR
        else:
            info.Copyright = "(C) 2007 %s, %s" % (appcfg.APP_AUTHOR, appcfg.APP_VENDOR)
        info.Description = wordwrap(appcfg.description, 350, wx.ClientDC(self))
        info.WebSite = (appcfg.SITE_URL[0], appcfg.SITE_URL[1])
        authorstr = appcfg.APP_AUTHOR
        if appcfg.APP_EMAIL:
            authorstr += " (%s)" % appcfg.APP_EMAIL
        info.Developers = [ authorstr ]
        info.License = wordwrap(appcfg.licensetext, 500, wx.ClientDC(self))
        wx.AboutBox(info)


    def _onGuiVisitSite(self, event):
        """ Execute the internet page as an external link """

        # use execute_uri
        if appcfg.SITE_URL[0]:
            wx.LaunchDefaultBrowser(appcfg.SITE_URL[0])
