#----------------------------------------------------------------------
# This file was generated by D:\personal\src\airs\gui\images\make_images.py
#
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib


def getData():
    return zlib.decompress(
'x\xda\x01\xc8\x027\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x02\x7fIDAT8\x8d\xc5\x93KkTg\x00\x86\x9f\xef\
\x9b3\'\x93\x99\xa3\x8cI\xc6\\&I\x93z\xa1`\x9a\x10\xbb\x10KQ"\xd8\x85\xa0\
\xe8\xae\xd2\xdf RJ\xa8.\xfb\x07\x84RH\x17]\xb9\xee\xa6b\xdb \xe8"`\x95\xa8M\
\n\xf1\xaei.c2\xc6\xc6d\x9cdf\xcew\xbe[\x17bP\\\xb6\xd0w\xf7n\x9ew\xf3\xbc\
\xf0\x7fG\xbc]\x16\x16\x16>K\xd9\xfay\xd1X\x1bA7\x9a\x853`\r8\x8b@*\xa2\xb6;\
.\xdf{\xaeX,^\x7f\x0f\xb0\xb8\xb8x1\x88_|!\xd5Z\x18\xca\x00\x9d\xc4T\xd6\xd7\
1IBS\n\n\xdbrX\xad\xd0\xd6y\xba\x87\x7fi\xdf=xb\x0bP*\x95\xae\xa4*\xb3\x9f\
\x87h\x9e-/S*\xaf\x11\x8b\x08\xdd\xd4\x81\xb6\x82\xc48rf\x85.\x96\x19\xe8iE:\
\x8b\xed\xfax\xa60xdP\xcc\xcf\xcf_\x08\xebK_\x85\xba\xca\xcc\xe3y\xc2\x0f\
\x0e\xf3,\xe9D\x1bP\xda\x13k\x8f\xd2\x8eF\xe2\x18\xe8\x0e\xf9h\xe3Wr\xd59\
\xa2t\x8aj\xff\xc8EQz2\xf3\\V\x1e\xb7\xbf\xf2y\xf6\x0c\x1fb|\xaaN\xa5\xeeP\
\xda3\xfa\xe5\x10\xde;F\xc7\xa6\x89\xb5#\x93\x16|s\xaa\x85\xd5\x07\x93\xb8\
\xbb\xe3\xacnj\x13\xe8\xb5\xd9\x9d\xd9\xce!\xfa\x0bE\xe0\xf5j]Y\x94\x01\xef\
\x1c\xde;\xea\x89E)\x87\xf0\x12\x80\xfc\x9eO\xa8e\xb7\xa3/\x8f\x05Az\xe7\x80\
\x0b\xa3\x96\x94\xb5\x16)%\xad\xdb\xa0\xf4\xd2\x12\'\x8e\xb3\xdf\xdfB%\x9ez\
\xc3\x10k\xc7\xbe\xde,\xce9\xac\xb5\xc8\x96n\xf2\xfd\xfb\xbcdc\xa9\xaa\xab+\
\x18c\xd0Z\xd3\xdb*\x89BG\xad\xae\xa95\x0c\xb5X\xb3\x19k\xda"\xc1p_\x80\xd6\
\x1ac\x0c\xaa<K\xaa\xb2\xa4\xa5\xcb\xb4\xfd\xe4\x9f\xdf\')\xfd\x89\xaa\xae\
\xd2\x9a\xb3\x1c\xd8%\xd9\xdb\xe1\t\xbc"M\xc2p\x8f\xe0\xf8\xfe\x90\xfe\x82 \
\xa9UQ\x8f~GO\xfcH9\xc9\xfc!\x00\x1eN\xdf\xbc\x91{y\xef`s p\xf9\xbeu\x91+\
\xc4>\xda\x91\x88 \xe3\xdex\xe2\xbd\xc7\xbd\xf8+\xe3\xe7&;\x93\xd2=\x1e5\xa2\
\xf2\xd1\xaf/\x14\xb7D\xba=q\xe5RR~r\xacC\xbe\n\xa2l\x06\x9a\xb6\xe3\xd2Y\
\xbc\x07\xe1\x0cfs\x1dV\x9e2\xf7\xf7\xa6\xdf\xd8\xf1\xe1\x9d\xec\xca\xb5OG\
\xbe\x9d0\xef\xa8\xfc\xdbwg\x9aLM\x9dTJ\x9dJ\x0bFB\xe1#\xe9\x9dp\xd6\xb8FCM\
\xc5*\xfeY\x1a=~\xfa\x87\xab\x0f\xfe\xbb7\xfd\xdb\xfc\x03\x96\x82UC\x9e\x96\
\xa8.\x00\x00\x00\x00IEND\xaeB`\x82C;U\xbc' )

def getBitmap():
    return BitmapFromImage(getImage())

def getImage():
    stream = cStringIO.StringIO(getData())
    return ImageFromStream(stream)

