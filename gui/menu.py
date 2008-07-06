import wx
from images import icon_add, icon_delete, icon_edit
from images import icon_main, icon_about
from images import icon_home, icon_help, \
                   icon_visit_site, icon_searches
from images import icon_default_layout
from images import icon_add, icon_delete, icon_edit
from images import icon_preferences ,to_download, downloading, \
                   icon_downloaded, icon_ready, icon_processed

NORMAL  = 1
CHECK   = 2

def create(parent):        
    """
    Creates the menu system for the application, and initializes the
    event handlers for it.
    """

    menuitems = { 
        "exit":         ("E&xit", "Exit", "Exit the application",
                         None, parent._onGuiExit, "Exit", NORMAL),
        "add_series":   ("&Add ...\tCtrl+N", "Add", "Add a new series",
                         icon_add.getBitmap(), parent._onGuiAddNew, "AddNew", NORMAL),
        "del_series":   ("&Edit ...\tCtrl+E", "Edit", "Edit Series properties", 
                         icon_edit.getBitmap(), parent._onGuiEdit, "Edit", NORMAL),
        "edit_series":  ("&Delete\tCtrl+D", "Delete", "Delete Series",          
                         icon_delete.getBitmap(), parent._onGuiDelete, "Delete", NORMAL),
        "preferences":  ("&Preferences ...", "Preferences", "Open the application preferences",
                         icon_preferences.getBitmap(), parent._onGuiShowOptions, "Options", NORMAL ),
        "clear_cache":  ("&Clear Cache", "Clear Cache", "Clear cache of one or all series",
                         None, parent._onClearCache, "ClearCache", NORMAL),
        "select_all":   ("&Select All\tCtrl+A", "Select All", "Select all episodes",
                         None, parent._onSelectAll, "SelectAll", NORMAL),
        "edit_episode": ("&Edit ...", "Edit Episode", "Edit selected episode",
                         None, parent._onGuiEdit, "EditEpisode", NORMAL),
        "searches":     ("Search &Engines ...", "Edit Search Engines", "Edit Search Engine properties",
                         icon_searches.getBitmap(), parent._onEditSearchEngines, "EditSearches", NORMAL),
        "restore":      ("&Restore Default Layout", "Restore Default Layout", "Restore default layout of windows",
                         icon_default_layout.getBitmap(), parent._onGuiRestoreLayout, "RestoreLayout", NORMAL),
        "toggle_sel":   ("Toggle View Selector", "Toggle View Selector", "Toggle View Selector",
                         None, parent._onGuiToggleWindow, "ToggleLeft", CHECK),
        "toggle_prog":  ("Toggle Progress Log", "Toggle Progress Log", "Hide or show Progress Log window",
                         None, parent._onGuiToggleWindow, "ToggleBottom", CHECK),
        "toggle_stat":  ("Toggle Statistics Window", "Toggle Statistics Window", "Hide or show Progress Statistics window",
                         None, parent._onGuiToggleWindow, "ToggleStat", CHECK),
        "to_tray":      ("Minimize to tray", "Minimize to tray", "Upon minimize, hide in system tray",
                         None, parent._onGuiMinimizeToTray, "TrayMinimize", CHECK),
        "help":         ("&Help ... ", "Help", "Show the application help",
                         icon_help.getBitmap(), parent._onGuiVisitSite, "", NORMAL),
        "visit_site":   ("&Visit Site ... ", "Visit Site", "Visit Project Site", 
                         icon_visit_site.getBitmap(), parent._onGuiVisitSite, "", NORMAL),
        "about":        ("&About ...", "About", "Show the about dialog",
                         None, parent._onGuiAbout, None, NORMAL),
        "s_todownload": ("&To Download", "Mark as To Download", "Mark as To Download",
                         to_download.getBitmap(), None, None, NORMAL),
        "s_download":   ("&Downloading", "Mark as Downloading", "Mark as Downloading",
                         downloading.getBitmap(), None, None, NORMAL),
        "s_downloaded": ("&Downloaded", "Mark as Downloaded", "Mark as Downloaded",
                         icon_downloaded.getBitmap(), None, None, NORMAL),
        "s_ready":      ("&Ready", "Mark as Ready", "Mark as Ready",
                         icon_ready.getBitmap(), None, None, NORMAL),
        "s_seen":       ("&Seen", "Mark as Seen", "Mark as Seen",
                         icon_processed.getBitmap(), None, None, NORMAL)
      }
    
    
    menutree = [ ("&File",    [ "preferences", "-", "exit" ] ),
                 ("&Series",  [ "add_series", "edit_series", "del_series", "-", "clear_cache" ] ),
                 ("&Episode", [ "select_all", "searches" ] ),
                 ("&Window",  [ "restore", "toggle_sel", "toggle_prog", "toggle_stat", "-", "to_tray" ] ),
                 ("&Help",    [ "help", "visit_site", "-", "about" ] )
               ]
    
 
    menutb = [ "add_series", "edit_series", "del_series", "-", "searches", "-",
               "s_todownload", "s_download", "s_downloaded", "s_ready", "s_seen" 
             ]
    
    
    # create menu
    parent._menuBar = wx.MenuBar()

    for mainmenu in menutree:
        mnu = wx.Menu()
        for submenu in mainmenu[1]:
            if submenu == "-":
                mnu.AppendSeparator()
            else:
                id = wx.NewId()
                ml = menuitems[submenu]
                if ml[6] == CHECK:
                    mt = wx.ITEM_CHECK
                else:
                    mt = wx.ITEM_NORMAL
                
                smenu = wx.MenuItem(mnu, id, ml[0], ml[2], mt)
                if ml[3]:
                    smenu.SetBitmap(ml[3])
                
                if ml[4]:
                    parent.Bind(wx.EVT_MENU, ml[4], smenu)
                    
                if ml[5] != "" and ml[5] is not None:
                    parent.__dict__["_menu"+ml[5]] = smenu
                mnu.AppendItem(smenu)
            
        parent._menuBar.Append(mnu, mainmenu[0])

    parent.SetMenuBar(parent._menuBar)
                        
    parent._toggleWindowLookup = {}
    parent._toggleWindowLookup[parent._menuToggleLeft.GetId()] = "viewselectpanel"
    parent._toggleWindowLookup[parent._menuToggleBottom.GetId()] = "progresslogpanel"
    parent._toggleWindowLookup[parent._menuToggleStat.GetId()] = "statisticspanel"
      
    TBFLAGS = (   wx.TB_HORIZONTAL
                  | wx.NO_BORDER
                  | wx.TB_FLAT
                  )
     
    tb = parent.CreateToolBar( TBFLAGS )
    tsize = (16,16)
    
    tb.SetToolBitmapSize(tsize)
    
    parent._toolLookup = dict()
    for submenu in menutb:
        if submenu == "-":
            tb.AddSeparator()
        else:
            tid = wx.NewId()
            ml = menuitems[submenu]
            if ml[3]:
                bmp = ml[3]
            else:
                bmp = wx.NullBitmap
            if ml[6] == CHECK:
                tb.AddCheckLabelTool(tid, ml[1], bmp, shortHelp = ml[1], longHelp = ml[2])
            else:
                tb.AddLabelTool(tid, ml[1], bmp, shortHelp = ml[1], longHelp = ml[2])
            if ml[4]:
                parent.Bind(wx.EVT_TOOL, ml[4], id = tid)
        
            parent._toolLookup[submenu] = tid
    tb.Realize()
