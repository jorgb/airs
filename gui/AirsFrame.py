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
from webserver import synccmd, reactor

import menu

# gui elements
import ViewSelectPanel
import StatisticsPanel
import ProgressLogPanel
import MainPanel
import SeriesDlg
import SearchEngineDlg
import AirsTrayIcon
import OptionsDlg

# images
from images import icon_main, icon_about

from webserver import webdispatch

class AirsFrame(wx.Frame):
    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._trayIcon = None                       

        self._connectSignals()

        # instantiate the GUI        
        menu.create(self)
        
        self._createWindows()
        self._createTrayIcon()
        self._createStatusBar()

        reactor.parent = self

        # generic application events
        self.Bind(wx.EVT_CLOSE, self._onGuiClose)
        self.Bind(wx.EVT_UPDATE_UI, self._onUpdateUI)
        self.Bind(synccmd.EVT_REACTOR_CALLBACK_COMMAND, self._onWebRequest)

        # setup our application title and icon
        self.SetTitle(appcfg.APP_TITLE)
        self.SetIcon(wx.Icon(os.path.join(appcfg.appdir, "airs.ico"), wx.BITMAP_TYPE_ICO))        
        self.Bind(wx.EVT_ICONIZE, self._onGuiIconize)

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
        self._trayIcon = AirsTrayIcon.AirsTrayIcon(self)

    def _createWindows(self):
        """
        Create the main window that this frame contains
        """
        self._panes = {}

        # tell AUI to manage this frame
        self._aui = wx.aui.AuiManager()
        self._aui.SetManagedWindow(self)


        # construct the left top panel
        self._aui.AddPane(ViewSelectPanel.ViewSelectPanel(parent = self), wx.aui.AuiPaneInfo().
                          Name("viewselectpanel").Caption("View Selector").MinSize(wx.Size(200,250)).
                          BestSize(wx.Size(150, 200)).Left().MaximizeButton(True))

        # construct the left bottom panel
        self._aui.AddPane(StatisticsPanel.StatisticsPanel(parent = self), wx.aui.AuiPaneInfo().
                          Name("statisticspanel").Caption("Statistics Panel").MinSize(wx.Size(200,250)).
                          BestSize(wx.Size(150, 200)).Left().MaximizeButton(True))

        # construct the bottom panel
        self._aui.AddPane(ProgressLogPanel.ProgressLogPanel(parent = self), wx.aui.AuiPaneInfo().
                          Name("progresslogpanel").Caption("Progress Log").MinSize(wx.Size(100,80)).
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
            series.update_period = 7

            dlg.guiToObject(series)

            viewmgr.add_series(series)

            # select the new series
            viewmgr.set_selection(series)

            # ask if this needs to be scheduled too
            if wx.MessageBox("Do you wish to run an update for this series?", 
                             "Question", wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                viewmgr.get_selected_series()

        dlg.Destroy()


    def _onQueryEditSeries(self, msg):

        series = db.store.get(series_list.Series, msg.data.series_id)
        self._doEditSeries(series)


    def _onGuiEdit(self, event = None):
        """ Event handler to edit a Series """

        # only edit when a genuine series is selected
        if viewmgr.series_active():
            sel_id = viewmgr._series_sel._selected_series_id
            if sel_id != -1:        
                series = db.store.get(series_list.Series, sel_id)
                self._doEditSeries(series)


    def _doEditSeries(self, series):
        if series:        
            dlg = SeriesDlg.SeriesDlg(self)
            dlg._editing = True

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


    def _onEditSearchEngines(self, event):
        dlg = SearchEngineDlg.SearchEngineDlg(self)
        dlg.ShowModal()
        dlg.Destroy()


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

        if self._trayIcon is not None:
            self._trayIcon.Destroy()
            self._trayIcon = None

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

        self._menuBar.Check(self._menuTrayMinimize.GetId(), 
                            appcfg.options[appcfg.CFG_TRAY_MINIMIZE])

        # sync the checkbox view based upon the view state of the panels
        for menu_id in self._toggleWindowLookup.iterkeys():
            pane = self._aui.GetPane(self._toggleWindowLookup[menu_id])
            self._menuBar.Check(menu_id, pane.IsShown())

        enabled = viewmgr._series_sel._selected_series_id != -1
        self._menuEdit.Enable(enabled)
        self._menuDelete.Enable(enabled)
        self._menuClearCache.Enable(enabled)


    def _saveWindowLayout(self):
        """
        Saves the window layout for later use
        """
        # save windows layout
        width, height = self.GetSize()
        appcfg.options[appcfg.CFG_LAYOUT_LAST] = self._aui.SavePerspective()
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
        appcfg.Write()  


    def _callbackTrayIcon(self, kind):
        """
        Create the taskbar popup menu, and handle the events 
        here, so we can redirect the most important events easier
        """
        if kind == AirsTrayIcon.SHOW_MENU:
            traymenu = wx.Menu()
            m1 = traymenu.Append(wx.NewId(), "&Restore Window")
            m1.Enable(self.IsIconized())

            traymenu.AppendSeparator()
            m2 = traymenu.Append(wx.NewId(), "&Exit")

            self.Bind(wx.EVT_MENU, self._onGuiRestore, m1)   
            self.Bind(wx.EVT_MENU, self._onGuiPreExit, m2)

            self.PopupMenu(traymenu)
            traymenu.Destroy()

        elif kind == AirsTrayIcon.ACTIVATE_WINDOW:
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, -1)
            self._onGuiRestore(evt)    


    def _onGuiRestore(self, event):
        """
        Restore action for window
        """
        if self.IsIconized():
            self.Iconize(False)
        if not self.IsShown():
            self.Show(True)
            appcfg.options[appcfg.CFG_LAYOUT_HIDDEN] = False
        self.Raise()    


    def _onGuiPreExit(self, event):
        """
        In this event we post another event to make sure that 
        the closing of the window is decoupled from the rest of 
        the code
        """
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, self._menuExit.GetId())
        wx.PostEvent(self, evt)


    # ============================ VARIOUS METHODS =============================


    def _onWebRequest(self, event):
        """ Handle request of the web browser plugin """
        id = event.callid
        cmd = event.cmd
        args = event.args

        viewmgr.app_log("Received command '%s' with id %i from web browser" % (cmd, id))

        webdispatch.execute(cmd, id, args)

    def _connectSignals(self):
        """
        Connects all the signals used in this application to members of this
        main frame. The view manager sends out signals when functionality of
        your application is called
        """
        Publisher().subscribe(self._onSignalSettingsChanged, signals.APP_SETTINGS_CHANGED)
        Publisher().subscribe(self._onQueryEditSeries, signals.QUERY_EDIT_SERIES)

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
            info.Copyright = "(C) 2008 %s" % appcfg.APP_AUTHOR
        else:
            info.Copyright = "(C) 2008 %s, %s" % (appcfg.APP_AUTHOR, appcfg.APP_VENDOR)
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
