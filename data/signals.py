APP_INITIALIZED      = ('app', 'initialized')        # is emitted when viewmgr.app_init is called
                                                     # should be sent AFTER all data is restored in 
                                                     # viewmgr.app_init
QRY_APP_CLOSE        = ('query', 'app', 'close')     # signal sent to ask if the application can close
                                                     # if the app can't close, call the QueryResult
                                                     # object with .deny() to dissallow closing
APP_CLOSE            = ('app', 'close')              # final call before window closes, when handling this
                                                     # signal all the actions must be completed, the 
                                                     # application WILL close after this call
APP_SETTINGS_CHANGED = ('app', 'settings', 'changed')   # sent when the settings are changed, submitted after
                                                        # a call to viewmgr.app_settings_changed() is made
APP_LOG              = ('app',    'log')
EPISODE_ADDED        = ('episode', 'added')
EPISODE_DELETED      = ('episode', 'deleted')
EPISODE_UPDATED      = ('episode', 'updated')
SERIES_DELETED       = ('series', 'deleted')
SERIES_ADDED         = ('series', 'added')
SERIES_SELECT        = ('series', 'selected')
SERIES_UPDATED       = ('series', 'updated')


# from data model
DATA_SERIES_RESTORED = ('data', 'series', 'added')

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
