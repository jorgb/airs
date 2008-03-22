import os
import os.path

import wx
from wx.lib.pubsub import Publisher
from gui import appcfg

# Signals constants are used in the view manager (and the rest of the 
# application to send around changes in the application.

is_closing = False

# query signal to allow application to veto the close event
SIGNAL_QRY_APP_CLOSE        = ('query', 'app', 'close')  
# final signal that app closes, the destroy follows after this event
SIGNAL_APP_CLOSE            = ('app', 'close')  
# signal to restore the application window
SIGNAL_APP_RESTORE          = ('app', 'restore')
SIGNAL_APP_SETTINGS_CHANGED = ('app', 'settings', 'changed')

class QueryResult(object):
    """
    This class is designed to act as a reference object. If a signal is
    sent with this QueryResult object as data member, a listener can 
    veto the action by calling deny(). Calling allow() will allow the 
    action, but it will only set the flag to true if no others have denied it 
    """
    def __init__(self, allow = True):
        self._result = allow
        self._denied = False

    def allowed(self):
        """ Return true when the action is allowed """
        return self._result

    def deny(self):
        """ Set the result to False """
        self._result = False
        self._denied = True

    def allow(self):
        """ Set the result to True but only if none others have denied it """
        if not self._denied:
            self._result = True


#===============================================================================

# All actions that the viewmanager can do are defined here. These actions can
# be called in the application to send around certain events

def app_close():
    """ 
    Sends a signal that closes the application. If the QueryResult object
    is set to veto the closure, the final signal is not sent
    """
    global is_closing
    
    is_closing = False
    res = QueryResult()
    Publisher().sendMessage(SIGNAL_QRY_APP_CLOSE, res)
    if res.allowed():
        is_closing = True
        Publisher.sendMessage(SIGNAL_APP_CLOSE)
    return res.allowed()
    

def app_settings_changed():
    """
    Call this to send a signal that informs all the views that the 
    application settings are changed. Every view using these settings 
    should investigate if their view needs to be updated
    """
    Publisher().sendMessage(SIGNAL_APP_SETTINGS_CHANGED)
    
    
def app_restore():
    """
    Sends a signal that the application needs to restore it's window
    """
    Publisher().sendMessage(SIGNAL_APP_RESTORE)
    
    

