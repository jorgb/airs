#----------------------------------------------------------------------
# This file was generated by D:\src\airs\gui\images\make_images.py
#
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib


def getData():
    return zlib.decompress(
'x\xda\x01\xc3\x02<\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x02zIDAT8\x8d\xa5\x92\xcdK\x94Q\x14\xc6\x9f\
\x19\xe7C\x1dGL\xad\x91\xb015\x13\x93(\xda\x18a\x19H\x86EP\x11mDZ\xb7\n\xa2\
\xda\x18\x11\xb8p\x11A\x7fB\x04\xb5ha$\xd4"\x0c\x14,\x95\xcc$\xb2\x9a\x11\
\xb5Ls\xcc\x11g\x9c\xaf\xf7\xbd\xf7\x9esZ\x986\xe6\xec:\xf0\xc0\xb9\xf7r\x7f\
\xe7>\xe7\\\xe0?\xc3\x91\xbd\x88\x8e\x9f|$,\x9d"\x02a\x06X \xb4\x9e\x0b\xf3f\
\xce\x86\xe6\x82\xed\x13U\x00\xe0\xca\x060IGIM\x07\x84\x05 \x86\x10\xfd\x95!\
\xa4\xa3\xef\x90\x89M%7.o\x01,\x8f\x9d\xe8\xf6\xf8\xeb\x9c`@\xaf<\x83h\x03\
\xd6\x1a\xa24\xdc\xe5\x17a\xc5\xbe \x13\x0fS\xb0}\xc2\x9f]\xd4\x99U\xfdV~\
\xc9!P\xfa+\xc4\x10D\xaf\xcb]~\x1e*9\x8fLl\n\xc2\xba\xfe\xdf\x1e8\x01`i\xa4\
\xf9\x92\xc7\x17\xf4\xc0\xe1\x01\xa5&!\x86\xc0d\x90Wt\x04\xacS\xb0bah+q\xb6\
\xea\xcc\xe4tN\x00\x98\x1fz\xfcu\x10\x93\x82\x18\xf3\xc7\xb3\x81\xd3\x1bDf5\
\x04;9\x7f\xb3\xfa\xdc\xc4\xcb\x9cSX\x1cnnr{\xcaF\xfc\x95\xedP\xd1>\xb0\xd2\
\x10\xad\xc1\x96\x05O\xe0\x02\xa2\xe1\xc7\x02b\xf5 \xe1\xf3\xa6\x8c\xc2\xf5\
\x82\xb4\xed"\x063\xc7\xeb;\xa7\x03.\x87\xe1>O\xd9~\x08i\xb8\x8aOC\xc8@\x0c\
\x01\x02\x88a\x94\xee\xbd\xec\x10\xa3\xbd\xf6\xc7\x17\xa8,o\xc0\xdd\x85q\xef\
\x1d\x1f\xa7\xdd\xa4\x8e\x01\x80\x8b\x85\xbd\xc9\x9f\x83\xf6\xe6\xbci]\xf7c\
\xc5^a\x05\xc5\x06\xca\x10v\x97\xd6\xa1\xa1\xa2\t\t+\x85k\xf3#\xf9\xda\xcdK\
\xdb>\xd2F|{~p\xe0\xdeZa\xcb\xa9\xc6+ a\x10\x13\x18\x82H|\x1e;|\xbb0<\xd3\
\x8f\xf7s\x83\xcc\x0e\xbb\xd4\x95\x0b \xcc-\x96Q a|_\x99\x82f\x03\xc3\x1a\
\x9a4\xd6\xec\x04\x0e\xef9\x8e\xa4N;Gg\x87V\xb6\x01fz\x1b?\xe4\xfb\xf7\xc1\
\x8a\x86a\xc8 P\x1c\x84a\x02\tc1>\x87\xd2\xa2\n\x8c\xffx\x83\xa1\xe9\xa1eEh\
\xdbb\xe1\xd3\xd3\x03E>W^B\x88q#\x9aF\xc6V\xa2X\xc12\n\xb5;\x1b\x1dGk\xda06\
\xf7\x16\xfd\xa1W\x11Eh\x8d\xf4\xe0\xf3\x96\x17\x148y\xd4(\xfae;\xf3j{\xaf\
\xce&\xb3\xcfV\xbb\x87S\x0egA\xe1@\xf8\xf5\x82q\xa05\xd2\x83\xd06\xef\xa1\'u\
M\xb9z\x02\x00\xd5\xb7\x91\nv\xe5I\xa0\x0b\xd5\xd9\xfb\xbf\x01P\xec\x88\xff\
\xb7$3\xaa\x00\x00\x00\x00IEND\xaeB`\x82\xf3E>\x9a' )

def getBitmap():
    return BitmapFromImage(getImage())

def getImage():
    stream = cStringIO.StringIO(getData())
    return ImageFromStream(stream)

