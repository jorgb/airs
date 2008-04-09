#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import wx
import wx.xrc as xrc
import os.path
from data import appcfg

def loadGuiResource(filename):
    """
    Load the XRC resource based upon the name
    """
    resname = os.path.join(appcfg.appdir, 'gui', filename)
    res = xrc.EmptyXmlResource()
    res.Load(resname)
    return res
