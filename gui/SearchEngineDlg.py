#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import sys
import wx
import wx.xrc as xrc
import xmlres
from data import appcfg
from data import viewmgr, db, searches
import SearchEngineItemDlg

class SearchEngineDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("SearchEngineDlg.xrc")
        res.LoadOnDialog(pre, parent, "SearchEngineDlg")
        self.PostCreate(pre)
        
        self._list = xrc.XRCCTRL(self, "ID_SEARCH_ENGINES")
        
        sel = self._list
        sel.InsertColumn(0, "Name", width = 80)
        sel.InsertColumn(1, "URL", width = 410)

        self._populateSearchEngines()
        
        self._add = xrc.XRCCTRL(self, "ID_ADD")
        self._edit = xrc.XRCCTRL(self, "ID_EDIT")
        self._delete = xrc.XRCCTRL(self, "ID_DELETE")
        
        self.Bind(wx.EVT_BUTTON, self._onOK,  xrc.XRCCTRL(self, "wxID_OK"))
        self.Bind(wx.EVT_BUTTON, self._onAdd, self._add)
        self.Bind(wx.EVT_BUTTON, self._onEdit, self._edit)
        self.Bind(wx.EVT_BUTTON, self._onDelete, self._delete)
        
        
    def _onAdd(self, event):
        dlg = SearchEngineItemDlg.SearchEngineItemDlg(self)
        s = searches.Searches()
        s.name = unicode("New Engine #%i" % (self._list.GetItemCount()))
        s.url = unicode('http://')
        dlg.objectToGui(s)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.guiToObject(s)
            db.store.add(s)
            db.store.commit()
            
            index = self._list.InsertStringItem(sys.maxint, '')
            self._list.SetItemData(index, s.id) 
            self._updateItem(index, s)

        dlg.Destroy()
        

    def _onEdit(self, event):
        idx = self._list.GetFirstSelected()
        if idx != wx.NOT_FOUND:
            s = db.store.find(searches.Searches, searches.Searches.id == self._list.GetItemData(idx)).one()
            if s:
                dlg = SearchEngineItemDlg.SearchEngineItemDlg(self)
                dlg.objectToGui(s)
                if dlg.ShowModal() == wx.ID_OK:
                    dlg.guiToObject(s)
                    db.store.commit()
                    self._updateItem(idx, s)
                dlg.Destroy()
                

    def _onDelete(self, event):
        idx = self._list.GetFirstSelected()
        if idx != wx.NOT_FOUND:
            res = wx.MessageBox("Are you sure you want to delete this engine?", "Question", 
                                wx.ICON_INFORMATION | wx.YES_NO)
            if res == wx.YES:                
                s = db.store.find(searches.Searches, searches.Searches.id == self._list.GetItemData(idx)).one()
                if s:
                    searches.delete_search(s)
                self._list.DeleteItem(idx)
                
        
    def _populateSearchEngines(self):
        
        sel = self._list
        result = db.store.find(searches.Searches)
        engines = [ eng for eng in result.order_by(searches.Searches.name) ]
        for eng in engines:
            index = sel.InsertStringItem(sys.maxint, '')
            sel.SetItemData(index, eng.id)            
            self._updateItem(index, eng)
            
            
    def _updateItem(self, index, eng):
        sel = self._list
        sel.SetStringItem(index, 0, eng.name)
        sel.SetStringItem(index, 1, eng.url)
        

    def _onOK(self, event): 
        event.Skip()

