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

menuItems = dict()
mainMenuLookup = dict()
mainToolLookup = dict()

parent = None

TBFLAGS = ( wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT )
TBSIZE  = (16, 16)


class MenuData(object):
    def __init__(self):
        self.id = -1
        self.data = None


def _createSubMenu(mnu, menulst, extramenus = None):
    menuIdLookup = dict()
    if extramenus is None:
        extramenus = dict()

    for submenu in menulst:
        if isinstance(submenu, tuple):
            smenu = wx.Menu()
            d = _createSubMenu(smenu, submenu[1], extramenus)
            menuIdLookup.update(d)
            mnu.AppendMenu(wx.NewId(), submenu[0], smenu)
        elif submenu == "-":
            mnu.AppendSeparator()
        else:
            if submenu in mainMenuLookup:
                id = mainMenuLookup[submenu].id
            else:
                id = wx.NewId()
            if submenu in menuItems:
                ml = menuItems[submenu]
            else:
                ml = extramenus[submenu]

            if ml[4] == CHECK:
                mt = wx.ITEM_CHECK
            else:
                mt = wx.ITEM_NORMAL

            smenu = wx.MenuItem(mnu, id, ml[0], ml[2], mt)
            if ml[3]:
                smenu.SetBitmap(ml[3])

            md = MenuData()
            md.id = id
            if len(ml) > 4:
                md.data = ml[5]
            else:
                md.data = None

            menuIdLookup[submenu] = md
            mnu.AppendItem(smenu)

    return menuIdLookup


def _createMainMenu(menulst, menuBar):
    global mainMenuLookup

    for mainmenu in menulst:
        mnu = wx.Menu()
        d = _createSubMenu(mnu, mainmenu[1])
        mainMenuLookup.update(d)
        menuBar.Append(mnu, mainmenu[0])


def _createToolBar(menulst, tb):
    global mainToolLookup

    for submenu in menulst:
        if submenu == "-":
            tb.AddSeparator()
        else:
            tid = wx.NewId()
            ml = menuItems[submenu]
            if ml[3]:
                bmp = ml[3]
            else:
                bmp = wx.NullBitmap
            if ml[4] == CHECK:
                tb.AddCheckLabelTool(tid, ml[1], bmp, shortHelp = ml[1], longHelp = ml[2])
            else:
                tb.AddLabelTool(tid, ml[1], bmp, shortHelp = ml[1], longHelp = ml[2])

            mainToolLookup[submenu] = tid


def create(parent, bindEvents):
    """
    Creates the menu system for the application, and initializes the
    event handlers for it.
    """
    global menuItems
    menuItems = {
        "exit":          ("E&xit", "Exit", "Exit the application", None, NORMAL),
        "add_series":    ("&Add Series...\tCtrl+N", "Add", "Add a new series", icon_add.getBitmap(), NORMAL),
        "edit_series":   ("&Edit Series...\tCtrl+E", "Edit", "Edit Series properties", icon_edit.getBitmap(), NORMAL),
        "del_series":    ("&Delete Series\tCtrl+D", "Delete", "Delete Series", icon_delete.getBitmap(), NORMAL),
        "preferences":   ("&Preferences ...", "Preferences", "Open the application preferences", icon_preferences.getBitmap(), NORMAL ),
        "clear_cache":   ("&Clear Cache", "Clear Cache", "Clear cache of one or all series", None, NORMAL),
        "select_all":    ("&Select All\tCtrl+A", "Select All", "Select all episodes", None,  NORMAL),
        "edit_episode":  ("&Edit Episode...", "Edit Episode", "Edit selected episode", icon_edit.getBitmap(), NORMAL),
        "searches":      ("Search &Engines ...", "Edit Search Engines", "Edit Search Engine properties", icon_searches.getBitmap(),  NORMAL),
        "restore":       ("&Restore Default Layout", "Restore Default Layout", "Restore default window layout", icon_default_layout.getBitmap(), NORMAL),
        "toggle_sel":    ("Toggle View Selector", "Toggle View Selector", "Toggle View Selector", None,  CHECK),
        "toggle_prog":   ("Toggle Progress Log", "Toggle Progress Log", "Hide or show Progress Log window", None, CHECK),
        "toggle_stat":   ("Toggle Statistics Window", "Toggle Statistics Window", "Hide or show Progress Statistics window", None, CHECK),
        "to_tray":       ("Minimize to tray", "Minimize to tray", "Upon minimize, hide in system tray", None, CHECK),
        "help":          ("&Help ... ", "Help", "Show the application help", icon_help.getBitmap(), NORMAL),
        "visit_site":    ("&Visit Site ... ", "Visit Site", "Visit Project Site", icon_visit_site.getBitmap(), NORMAL),
        "about":         ("&About ...", "About", "Show the about dialog", None,  NORMAL),
        "s_todownload":  ("&To Download", "Mark as To Download", "Mark as To Download", to_download.getBitmap(), NORMAL),
        "s_download":    ("&Downloading", "Mark as Downloading", "Mark as Downloading", downloading.getBitmap(), NORMAL),
        "s_downloaded":  ("Down&loaded", "Mark as Downloaded", "Mark as Downloaded", icon_downloaded.getBitmap(), NORMAL),
        "s_ready":       ("&Ready", "Mark as Ready", "Mark as Ready", icon_ready.getBitmap(), NORMAL),
        "s_seen":        ("&Seen", "Mark as Seen", "Mark as Seen", icon_processed.getBitmap(), NORMAL)
      }

    mainmenu = [ ("&File",    [ "preferences", "-", "exit" ] ),
                 ("&Series",  [ "add_series", "edit_series", "del_series", "-", "clear_cache" ] ),
                 ("&Episode", [ "select_all", "searches", "-",
                                   ( "&Mark Status As", [ "s_todownload", "s_download",
                                                          "s_downloaded", "s_ready", "s_seen"] )
                              ] ),
                 ("&Window",  [ "restore", "toggle_sel", "toggle_prog", "toggle_stat", "-", "to_tray" ] ),
                 ("&Help",    [ "help", "visit_site", "-", "about" ] )
               ]

    toolmenu = [ "add_series", "edit_series", "del_series", "-", "searches", "-",
                 "s_todownload", "s_download", "s_downloaded", "s_ready", "s_seen"
             ]


    # create menu
    mb = wx.MenuBar()
    _createMainMenu(mainmenu, mb)
    parent.SetMenuBar(mb)

    # create toolbar
    tb = parent.CreateToolBar( TBFLAGS )
    tb.SetToolBitmapSize( TBSIZE )
    _createToolBar(toolmenu, tb)
    tb.Realize()

    # bind all events
    for evtid, evthnd in bindEvents:
        if evtid in mainMenuLookup:
            parent.Bind(wx.EVT_MENU, evthnd, id = mainMenuLookup[evtid].id)
        if evtid in mainToolLookup:
            parent.Bind(wx.EVT_TOOL, evthnd, id = mainToolLookup[evtid])


def populate(mnu, menulst, extramenus):
    """ Populates a submenu with a given definition list. If the
        items in this list are known by the submenu, they will get
        the same ID so that e.g. popup menu's can trigger the same
        handler as the main menu can """
    return _createSubMenu(mnu, menulst, extramenus)


def enable(parent, menu, enabled):
    """ Enables or disables a menu item by reference. menu can be a list or a
        single string """

    tb = parent.GetToolBar()
    mb = parent.GetMenuBar()

    if isinstance(menu, list):
        for id in menu:
            if id in mainToolLookup:
                tb.EnableTool(mainToolLookup[id], enabled)
            if id in mainMenuLookup:
                mb.Enable(mainMenuLookup[id].id, enabled)
    else:
        if menu in mainToolLookup:
            tb.EnableTool(mainToolLookup[menu], enabled)
        if menu in mainMenuLookup:
            mb.Enable(mainMenuLookup[menu].id, enabled)


def check(parent, id, value):
    """ Checks or unchecks a menu item """

    if id in mainToolLookup:
        tb = parent.GetToolBar()
        tb.ToggleTool(mainToolLookup[id], value)

    if id in mainMenuLookup:
        mb = parent.GetMenuBar()
        mb.Check(mainMenuLookup[id].id, value)

def getmenu(id):
    """ Returns the string by this menu item. The ID must be unique """

    for menu in mainMenuLookup.iterkeys():
        if mainMenuLookup[menu].id == id:
            return menu
    for menu in mainToolLookup.iterkeys():
        if mainToolLookup[menu] == id:
            return menu
    return None

def menuid_to_data(mnuid, menuLookup = None):
    """ Scans in the menu lookup (or main menu) for the ID returning the
        data that belongs to it """
    if menuLookup is None:
        menuLookup = mainMenuLookup
    for data in menuLookup.itervalues():
        if data.id == mnuid:
            return data.data
        