#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os.path
import wx

# the title of the application as it appears in the about box, window title etc
APP_TITLE           = "Airs:: Automatic Series Monitor"

# The version is used in the about box and title. Increment this with
# every release, but do not add the 'v' to the string
APP_VERSION         = "1.0"

# the name of the default database
DB_NAME             = 'airs.db'

# The application name on disk, same as the main startup file used for writing
# your settings to disk, the registry key, etc
APP_NAME            = 'Airs'

# generic author information
APP_AUTHOR          = 'Jorgen Bodde'
APP_EMAIL           = 'jorgb@xs4all.nl'
APP_VENDOR          = 'ImpossibleSoft'

# configuration values
CFG_LAYOUT_DEFAULT   = 'window/default_layout'       # default layout upon saving (saved one time only)
CFG_LAYOUT_LAST      = 'window/last_layout'          # last layout when closing window
CFG_LAYOUT_LAST_H    = 'window/last_height'          # last height when closing window
CFG_LAYOUT_LAST_W    = 'window/last_width'           # last width when closing window
CFG_LAYOUT_LAST_X    = 'window/last_xpos'            # last height when closing window
CFG_LAYOUT_LAST_Y    = 'window/last_ypos'            # last width when closing window
CFG_SHOW_UNSEEN      = 'series/show_unseen'
CFG_EPISODE_DELTA    = 'series/episode_delta'
CFG_UPDATED_VIEW     = 'series/updated_view'

configs = [ (CFG_LAYOUT_LAST_W,         'i', 700  ),
            (CFG_LAYOUT_LAST_H,         'i', 600  ),
            (CFG_LAYOUT_LAST,           's', ''   ),
            (CFG_LAYOUT_DEFAULT,        's', ''   ),
            (CFG_LAYOUT_LAST_X,         'i', -1   ),
            (CFG_LAYOUT_LAST_Y,         'i', -1   ),
            (CFG_SHOW_UNSEEN,           'b', False),
            (CFG_UPDATED_VIEW,          'i', 0    ),
            (CFG_EPISODE_DELTA,         'i', 0    ) ]

# max files in the file history
MAX_HISTORY_FILES   = 10

# Fill in the description of the application here
description = ""

SITE_URL = ("http://www.xs4all.nl/~jorgb/wb/MyProjects(2f)Airs.html", "%s Project Page" % APP_TITLE)

licensetext = """
Based upon GNU GENERAL PUBLIC LICENSE, Version 2, June 1991
For full text, see LICENSE.txt
"""

# placeholder for application directory (where script is started from)
appdir = ''

#-------------------------------------------------------------------------------
__cfg = None
options = {}

# TODO: On linux, the app should get a subdirectory first
def Get():
    global __cfg, options
    if not __cfg:
        if 'wxGTK' in wx.PlatformInfo:
            # force a file config, because our local config dir is similar to the
            # app name and the default is not the registry like Windows
            __cfg = wx.FileConfig(APP_NAME, APP_VENDOR,
                                  localFilename = '.' + 'airs' + '.cfg')
        else:
            # let wxWidgets deal with the way to store configs
            __cfg = wx.Config()
            __cfg.AppName = APP_NAME
            __cfg.VendorName = APP_VENDOR

    return __cfg


def Read():
    global options
    """
    Reads the config and stores it in the dictionary, with all defaults in place
    """

    # read all configuration variables
    cfg = Get()
    for ckey, ctype, cdef in configs:
        if ctype == 's':
            options[ckey] = cfg.Read(ckey, cdef)
        elif ctype == 'i':
            options[ckey] = cfg.ReadInt(ckey, cdef)
        elif ctype == 'b':
            options[ckey] = cfg.ReadInt(ckey, cdef) != 0
        elif ctype == 'l':
            lst = cfg.Read(ckey, cdef).split('|')
            options[ckey] = lst
        else:
            raise Exception, "Can't read type '%s' for key '%s'" % (ctype, ckey)


def Write():
    global options
    """
    Write the configuration. It writes all keys dynamically to the
    configuration. This has as advantage that config keys set by
    the application somewhere can also be stored, and it beats summing them
    all up
    """

    # config is dynamically written
    cfg = Get()
    for key, ctype, cdef in configs:
        if ctype == 'b':
            if options[key]:
                val = 1
            else:
                val = 0
            cfg.WriteInt(key, val)
        elif ctype == 'i':
            cfg.WriteInt(key, options[key])
        elif ctype == 'l':
            s = '|'.join(options[key])
            cfg.Write(key, s)
        elif ctype == 's':
            cfg.Write(key, options[key])
        else:
            raise Exception, "Can't write type '%s' for key '%s'" % (ctype, ckey)
    cfg.Flush()
