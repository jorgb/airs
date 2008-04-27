#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os.path
import sys

import wx
import wx.aui
from wx.lib.wordwrap import wordwrap
from wx.lib.pubsub import Publisher

from data import appcfg, viewmgr, signals
from data import series_list, db, series_filter

# gui elements
import ViewSelectPanel
import ProgressLogPanel
import MainPanel
import SeriesDlg

# images
from images import icon_main, icon_about
from images import icon_home, icon_help, \
                   icon_visit_site
from images import icon_default_layout
from images import icon_add, icon_delete, icon_edit


class AirsFrame(wx.Frame):
    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._connectSignals()
        
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

        self._toggleWindowLookup = {}

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
        self._menuAddNew = wx.MenuItem(mnu, wx.NewId(), "&Add ...\tCtrl+N", 
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


        # Episode menu
        mnu = wx.Menu()
        self._menuSelectAll = wx.MenuItem(mnu, wx.NewId(), "Select All\tCtrl+A", 
                                          "Select all episodes", wx.ITEM_NORMAL)
        mnu.AppendItem(self._menuSelectAll)

        #self._menuEdit = wx.MenuItem(mnu, wx.NewId(), "&Edit ...\tCtrl+E", 
        #                             "Edit Series properties", wx.ITEM_NORMAL)
        #self._menuEdit.SetBitmap(icon_edit.getBitmap())
        #mnu.AppendItem(self._menuEdit)

        #self._menuDelete = wx.MenuItem(mnu, wx.NewId(), "&Delete\tCtrl+D", 
        #                               "Delete this Series", wx.ITEM_NORMAL)
        #self._menuDelete.SetBitmap(icon_delete.getBitmap())
        #mnu.AppendItem(self._menuDelete)    

        #mnu.AppendSeparator()
        #self._menuClearCache = wx.MenuItem(mnu, wx.NewId(), "&Clear Cache", 
        #                                   "Clear cache of one or all series", wx.ITEM_NORMAL)
        #mnu.AppendItem(self._menuClearCache)    
        self._menuBar.Append(mnu, "&Episode")
        
        # window layout menu
        mnu = wx.Menu()                          
        self._menuRestoreLayout = wx.MenuItem(mnu, wx.NewId(), "&Restore Default Layout", 
                                              "Restore default layout of windows", wx.ITEM_NORMAL)
        self._menuRestoreLayout.SetBitmap(icon_default_layout.getBitmap())
        mnu.AppendItem(self._menuRestoreLayout)
        mnu.AppendSeparator()

        self._menuToggleLeft = wx.MenuItem(mnu, wx.NewId(), "Toggle View Selector", 
                                           "Hide or show View Selector window", wx.ITEM_CHECK)
        mnu.AppendItem(self._menuToggleLeft)
        self._toggleWindowLookup[self._menuToggleLeft.GetId()] = "viewselectpanel"
        
        self._menuToggleBottom = wx.MenuItem(mnu, wx.NewId(), "Toggle Progress Log", 
                                             "Hide or show Progress Log window", wx.ITEM_CHECK)
        mnu.AppendItem(self._menuToggleBottom)
        self._toggleWindowLookup[self._menuToggleBottom.GetId()] = "progresslogpanel"
        
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


        # initialize menu event handlers
        self.Bind(wx.EVT_MENU, self._onGuiAbout, self._menuHelpAbout)
        self.Bind(wx.EVT_MENU, self._onGuiExit, self._menuExit)
        self.Bind(wx.EVT_MENU, self._onGuiVisitSite, self._menuHelpVisitSite)
        self.Bind(wx.EVT_MENU, self._onGuiVisitSite, self._menuHelp)

        self.Bind(wx.EVT_MENU, self._onGuiRestoreLayout, self._menuRestoreLayout)

        self.Bind(wx.EVT_MENU, self._onGuiToggleWindow, self._menuToggleBottom)
        self.Bind(wx.EVT_MENU, self._onGuiToggleWindow, self._menuToggleLeft)
        
        self.Bind(wx.EVT_MENU, self._onGuiAddNew, self._menuAddNew)
        self.Bind(wx.EVT_MENU, self._onGuiEdit, self._menuEdit)
        self.Bind(wx.EVT_MENU, self._onGuiDelete, self._menuDelete)
        self.Bind(wx.EVT_MENU, self._onClearCache, self._menuClearCache)
        self.Bind(wx.EVT_MENU, self._onSelectAll, self._menuSelectAll)
    
        
    def _createWindows(self):
        """
        Create the main window that this frame contains
        """
        self._panes = {}

        # tell AUI to manage this frame
        self._aui = wx.aui.AuiManager()
        self._aui.SetManagedWindow(self)

        
        # construct the left panel
        self._aui.AddPane(ViewSelectPanel.ViewSelectPanel(parent = self), wx.aui.AuiPaneInfo().
                          Name("viewselectpanel").Caption("View Selector").MinSize(wx.Size(150,200)).
                          BestSize(wx.Size(150, 200)).Left().MaximizeButton(True))
        
        # construct the bottom panel
        self._aui.AddPane(ProgressLogPanel.ProgressLogPanel(parent = self), wx.aui.AuiPaneInfo().
                          Name("progresslogpanel").Caption("Progress Log").MinSize(wx.Size(100,50)).
                          Bottom().MaximizeButton(True))
        
        # construct the middle part
        self._aui.AddPane(MainPanel.MainPanel(parent = self), wx.aui.AuiPaneInfo().
                          Name("mainpanel").Caption("Main Window").
                          CenterPane().CloseButton(False).MaximizeButton(True))
        self._aui.Update()
        
        
    def _createStatusBar(self):
        """
        Creates a status bar on the current frame
        """
        # specify your statusbar here, add more fields if needed
        self._statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self._statusbar.SetStatusWidths([-1, -1])            
    
    
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
        
        # only edit when a genuine series is selected
        if viewmgr.series_active():
            sel_id = viewmgr._series_sel._selected_series_id
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

        if viewmgr.series_active():
            sel_id = viewmgr._series_sel._selected_series_id
            if sel_id != -1:
                series = db.store.get(series_list.Series, sel_id)
        
                if wx.MessageBox("Are you sure you want to delete this series?\n" + \
                                 "All gathered episodes will also be lost!", "Warning", wx.ICON_WARNING | wx.YES_NO) == wx.YES:
                    # delete 
                    viewmgr.delete_series(series)
    
                    
    def _onSelectAll(self, event):
        viewmgr.select_all_episodes()
                    
                    
    def _onClearCache(self, event):
        """
        Clear cache of one or all items
        """
        if viewmgr.series_active():
            if wx.MessageBox("Clearing the cache means that from this series, the downloaded episodes will\n" + \
                             "be deleted. On the next update, the series will be refreshed again.\n" + \
                             "Be aware that earlier downloaded items not found on the webpage(s), are lost forever.\n" +
                             "Would you like to do this?", "Warning", wx.ICON_WARNING | wx.YES_NO) == wx.YES:
                viewmgr.clear_current_cache()
    
    # ============================= CLOSE METHODS ==============================
    
    def _onGuiExit(self, event):
        """ 
        Attempt to close the main window
        """
        self.Close()


    def _onGuiClose(self, event):
        """
        Last moment to save anything, let's do it here
        """
        self._saveWindowLayout()
        viewmgr.app_close()
        viewmgr.app_destroy()
        event.Skip()

    # ============================== AUI METHODS ===============================

    def _onGuiRestoreLayout(self, event):
        pers = appcfg.options[appcfg.CFG_LAYOUT_DEFAULT]
        if pers:
            self._aui.LoadPerspective(pers, True)


    def _onGuiToggleWindow(self, event):
        if event.GetId() in self._toggleWindowLookup:
            pane = self._aui.GetPane(self._toggleWindowLookup[event.GetId()])
            if pane:
                pane.Show(not pane.IsShown())
        self._aui.Update()



    # ==================== LAYOUT AND UI UPDATE METHODS ========================
    
    def _onUpdateUI(self, event):
        """
        This event is called periodically to allow the user to update the
        menu / toolbar / buttons based upon the internal application state.
        """

        # sync the checkbox view based upon the view state of the panels
        for menu_id in self._toggleWindowLookup.iterkeys():
            pane = self._aui.GetPane(self._toggleWindowLookup[menu_id])
            self._menuBar.Check(menu_id, pane.IsShown())

        # TODO: Add your enable / disable control code here
        pass

    
    def _saveWindowLayout(self):
        """
        Saves the window layout for later use
        """
        # save windows layout
        width, height = self.GetSize()
        appcfg.options[appcfg.CFG_LAYOUT_LAST] = self._aui.SavePerspective()

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

        # store default perspective if needed, and load
        # last perspective used if present
        pers = appcfg.options[appcfg.CFG_LAYOUT_DEFAULT]
        if not pers:
            appcfg.options[appcfg.CFG_LAYOUT_DEFAULT] = self._aui.SavePerspective()
        else:
            pers = appcfg.options[appcfg.CFG_LAYOUT_LAST]
            if pers:
                self._aui.LoadPerspective(pers)
        
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
