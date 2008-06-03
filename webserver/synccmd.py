import wx
import  wx.lib.newevent

# event used to call back to GUI for synchronized db access
SyncCallbackCommandEvent, EVT_REACTOR_CALLBACK_COMMAND = wx.lib.newevent.NewCommandEvent()

_callid = 0
def getCallID():
    """
    Returns a new ID to which can be referenced 
    """
    global _callid
    
    _callid += 1
    return _callid


class SyncResultBase(object):
    def __init__(self, id):
        self.id = id             # ID of caller
