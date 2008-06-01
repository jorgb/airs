import xml.etree.ElementTree as et
from data import series_list
from data import db

def get_series_xml():
    """
    This function returns an XML structure that contains all the series
    that are currently in airs, with all properties needed for XSLT -> HTML
    """
    
    root = et.Element("airs")
    items = et.SubElement(root, "series")
    
    result = db.store.find(series_list.Series).order_by(series_list.Series.name)
    series = [serie for serie in result]
    
    for item in series:
        serie = et.SubElement(items, "item")
        serie.attrib["name"] = item.name
        serie.attrib["id"] = str(item.id)
        serie.attrib["cancelled"] = str(item.postponed)

    s = "<?xml version='1.0' encoding='utf-8'?>" + et.tostring(root)
    f = open("D:\\series.xml", "wt")
    f.write(s)
    f.close()
    
    return s
    
    