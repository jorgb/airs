import wx
import  wx.lib.newevent
import threading
import time

# event used to call back to GUI for synchronized db access
SyncCallbackCommandEvent, EVT_REACTOR_CALLBACK_COMMAND = wx.lib.newevent.NewEvent()


class SyncCommand(object):
    def __init__(self, id):
        self.id = id             # ID of caller
        self.params = dict()
        self.html = ''
        

class SyncCommandList(object):
    def __init__(self):
        self.__list = []
        self.__lock = threading.Lock()

        
    def getCmd(self, id):
        """ Returns None if obj.id is not present, else obj and removes it """
        self.__lock.acquire()
        try:
            result = None
            for o in self.__list:
                if o.id == id:
                    result = o
            if result is not None:
                self.__list.remove(o)                
        finally:
            self.__lock.release()
        return result

    
    def putCmd(self, cmd):
        """ Puts command in list """
        self.__lock.acquire()
        try:
            self.__list.append(cmd)
        finally:
            self.__lock.release()
    
        
_callid = 0
def getCallID():
    """
    Returns a new ID to which can be referenced 
    """
    global _callid
    
    _callid += 1
    return _callid


TIME_CHUNK = 50
def waitForResponse(id, msec):
    """ Wait for a timed response in 50 msec intervals """
    sl = get()
    trials = (msec / TIME_CHUNK) + 1
    while trials > 0:
        cmd = sl.getCmd(id)
        if cmd is not None:
            return cmd
        time.sleep(TIME_CHUNK / 1000.0)
    return None

#===============================================================================

_synclist = None
def get():
    global _synclist
    if _synclist is None:
        _synclist = SyncCommandList()
    return _synclist