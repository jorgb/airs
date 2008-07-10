#----------------------------------------------------------------------
# This file was generated by D:\src\airs\gui\images\make_images.py
#
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib


def getData():
    return zlib.decompress(
'x\xda\x01\xfe\x01\x01\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\
\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\
\x08\x08\x08\x08|\x08d\x88\x00\x00\x01\xb5IDAT8\x8d\xb5S=H\x9bQ\x14=\xfe\x14\
\x15!\x16J\xe2\xa0\xd1`C\xd1\x18+Q\x84,j\xfck@\xa1\x14$C\xe9R\xa7\x80\xa8K\
\xbau\x91\xce.\x82 H\x97\xba\x08\xd1Et\xd1\xa8$\x8a\x9a%\x94*\x89\x89Qc\n\
\xa5\x88\x1d\xba\xa9\xef\xde\xfb}\x9dR\xbe\xd2~\x8dPz\xa6w\xdf\xb9\xefp8\x87\
\x07\xfcoL\xee\x8c\x85\x03\xe1@\x99\x19_ZL\x80\x147[\xaa\x1el\x9b\xf1%\xc6!t\
\x18\xf4\xe9\xa2O\x0bK/\xb3\x80IPW]\x0ffF\xf6\xeb\xe9\xe6\xd2\xabU\xbf\xa9@\
\xe80\xe8\x13\xd6f\xdc5\xed\x9d\xb6\xcaZ\x88.\xd0t\x81h\x02\xd1\x05\x89\\\
\x02\x99\xcf\x99\xf3\xb5\xf1\x88\xd3(P^8\xb0\xd2^6[Z:\xad\x156|\xba\xfa\x88\
\x8bo\xe7 E\xa8\xb7\xd8\xc1\xccH\xe7O\xb7\xd6\'"C\xa6\x0e&\xb6^_2K#\x93@)\
\xda[\x1c]\xee\x01\x80\x17\x0b\xfe#\xa5\xf8{\xd7\xf5\xb6o\xc3\xe2\xad\x88\
\x87\xe27\xc5r\x831\xf5\xe1\xd9\xfe\x95\xbf\xb5`\x8a\xe7\xf3C+\xf7\xd9+7\x0e\
\x81p\xa0\xca\x95t\xdd%\xac\xfb\xd1\xdb[zX\xb8\xf7\xbe\xf5\xec\x92\xe2nR\x0c\
V\x9cO\xcdg\x1d\x05\xee\x97\x1a\x01`d\xae?\xd2hu\x0c\x12\x11Rgi\x90b4\xd9\
\x1d\xe8\xf2x\x90\xcad\x10\xdb;X8{\x9f\x0b\xfe\xd1\xc1\xf0l\xdf\x95\xfdQ\x83\
\xad\xcd\xd9\n\xd1\x04\xee\'\xae\x9fufs\x17\x88\xc5\xf6\x13$\xb4d|\xf3\x9b\
\x83\x9ew\xde\rG]\xc33fA2}\x02V\x0c&\x011\xc7Dx:\xff\xe1K\xb4h0\x1do\xda\xa2\
O\xa7Z\x8e\x8a.\xc2\xe4/<\xce\x1f\x0f(\xe2\xf4}\x04\xfe\x19?\x00\xb3\x80\xcf\
=\xb3O\xff^\x00\x00\x00\x00IEND\xaeB`\x82)\xde\xe6\x1e' )

def getBitmap():
    return BitmapFromImage(getImage())

def getImage():
    stream = cStringIO.StringIO(getData())
    return ImageFromStream(stream)
