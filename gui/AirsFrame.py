#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os.path
import sys

import wx
from wx.lib.wordwrap import wordwrap
from wx.lib.pubsub import Publisher

from data import appcfg, viewmgr, signals
from data import series_list, db

# gui elements
import MainPanel
import SeriesDlg

# images
from images import icon_main, icon_about
from images import icon_home, icon_help, \
                   icon_visit_site
from images import icon_add, icon_delete, icon_edit

class AirsFrame(wx.Frame):
    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        # instantiate the GUI
        self._createMenu()
        self._createWindows()
        self._createStatusBar()

        # generic application events
        self.Bind(wx.EVT_CLOSE, self._onGuiClose)
        self.Bind(wx.EVT_UPDATE_UI, self._onUpdateUI)

        # setup our application title and icon
        self.SetTitle(appcfg.APP_TITLE)
        self.SetIcon(wx.IconFromBitmap(icon_main.getBitmap()))

        # put windows like they were the last time
        self._restoreWindowLayout()
                
        # init viewmgr (always do this last so that
        # signals to be emitted can access controls)
        viewmgr.app_init()
        
        self._connectSignals()
                
        # periodic GUI update timer
        self.tmr = wx.Timer(self)
        self.tmr.Start(500)
        self.Bind(wx.EVT_TIMER, self._onTimer, self.tmr)
        
    # ========================== GUI CREATION CODE =============================

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

        mnu.AppendSeparator()
        
        self._menuClearCache = wx.MenuItem(mnu, wx.NewId(), "&Clear Cache", 
                                       "Clear cache of one or all series", wx.ITEM_NORMAL)
        mnu.AppendItem(self._menuClearCache)    
        
        self._menuBar.Append(mnu, "&Series")

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
        self.Bind(wx.EVT_MENU, self._onGuiExit, self._menuExit)
        self.Bind(wx.EVT_MENU, self._onGuiVisitSite, self._menuHelpVisitSite)

        self.Bind(wx.EVT_MENU, self._onGuiAddNew, self._menuAddNew)
        self.Bind(wx.EVT_MENU, self._onGuiEdit, self._menuEdit)
        self.Bind(wx.EVT_MENU, self._onGuiDelete, self._menuDelete)
        self.Bind(wx.EVT_MENU, self._onClearCache, self._menuClearCache)
    
        
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
        """ Event handler to add a new Series """

        dlg = SeriesDlg.SeriesDlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            # we instantiate a new series object
            series = series_list.Series()
            dlg.guiToObject(series)
            
            viewmgr.add_series(series)
            
            # select the new series
            viewmgr.set_selection(series)

            # ask if this needs to be scheduled too
            if wx.MessageBox("Do you wish to run an update for this series?", 
                             "Question", wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                viewmgr.get_selected_series()
            
        dlg.Destroy()


    def _onGuiEdit(self, event):
        """ Event handler to edit a Series """

        sel_id = viewmgr._series_sel._selection_id
        if sel_id != -1:        
            dlg = SeriesDlg.SeriesDlg(self)
            dlg._editing = True
            
            series = db.store.get(series_list.Series, sel_id)
            dlg.objectToGui(series)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.guiToObject(series)
                viewmgr.update_series(series)
            
            dlg.Destroy()

        
    def _onGuiDelete(self, event):
        """ Event handler for deleting a Series """

        sel_id = viewmgr._series_sel._selection_id
        if sel_id != -1:
            series = db.store.get(series_list.Series, sel_id)
    
            if wx.MessageBox("Are you sure you want to delete this series?\n" + \
                             "All gathered episodes will also be lost!", "Warning", wx.ICON_WARNING | wx.YES_NO) == wx.YES:
                # delete 
                viewmgr.delete_series(series)
    

    def _onClearCache(self, event):
        """
        Clear cache of one or all items
        """
        
        if wx.MessageBox("Clearing the cache means that the downloaded series the selected\n" + \
                         "series will be lost. The next update, the series will be refreshed again.\n" + \
                         "Be aware that earlier downloaded items not found on the webpage, are lost forever.\n" +
                         "Would you like to do this?", "Warning", wx.ICON_WARNING | wx.YES_NO) == wx.YES:
            viewmgr.clear_current_cache()
            
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

        event.Skip()            


    # ==================== LAYOUT AND UI UPDATE METHODS ========================
    
    def _onUpdateUI(self, event):
        """
        This event is called periodically to allow the user to update the
        menu / toolbar / buttons based upon the internal application state.
        """
        
        if viewmgr._series_sel._selection_id != -1:
            has_selection = True
        else:
            has_selection = False        
        self._menuEdit.Enable(has_selection)
        self._menuDelete.Enable(has_selection)
        self._menuClearCache.Enable(has_selection)
        pass
    
        
    def _saveWindowLayout(self):
        """
        Saves the window layout for later use
        """
        # save windows layout
        width, height = self.GetSize()

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
        

    def _onTimer(self, event):
        """
        Periodic check function to update various GUI elements.
        We could use OnGUIUpdate but it is sent too sporadically
        """
        series_title = viewmgr.get_current_title()        
        if series_title:
            self._statusbar.SetStatusText("Processing: %s" % series_title, 1)
        else:
            if viewmgr.is_busy():
                self._statusbar.SetStatusText("Working hard ..", 1)
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
        Publisher().subscribe(self._onSignalSettingsChanged, signals.APP_SETTINGS_CHANGED)


    def _onSignalSettingsChanged(self, msg):
        """
        Act upon a change of settings. In here you can update the GUI controls
        that need updating
        """
        # TODO: Implement to reflect changed settings
        pass


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
