import libxml2
from data import series_list
from data import db

def get_series_xml():
    """
    This function returns an XML structure that contains all the series
    that are currently in airs, with all properties needed for XSLT -> HTML
    """
    
    dom = libxml2.newDoc("1.0")
        
    root = libxml2.newNode("airs")
    dom.addChild(root)
    
    items = libxml2.newNode("series")
    root.addChild(items)
        
    result = db.store.find(series_list.Series).order_by(series_list.Series.name)
    series = [serie for serie in result]
    
    for item in series:
        serie = libxml2.newNode("item")

        serie.setProp("name", item.name)
        serie.setProp("id", str(item.id))
        serie.setProp("cancelled", str(item.postponed))

        # report total number of episodes and the 
        # episodes already seen
        c = db.store.execute("select count(*) from episode where series_id = %i" % item.id)
        totalcount = str(c.get_one()[0])
        
        c = db.store.execute("select count(*) from episode where series_id = %i and status = 4" % item.id)
        seencount = str(c.get_one()[0])
        
        serie.setProp("seencount", seencount)
        serie.setProp("count", totalcount)
        
        items.addChild(serie)

    return dom
    
    