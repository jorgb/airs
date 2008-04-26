#----------------------------------------------------------------------
# This file was generated by D:\personal\src\airs\gui\images\make_images.py
#
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib


def getData():
    return zlib.decompress(
'x\xda\x01z\x02\x85\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x021IDAT8\x8du\x92AKTQ\x14\x80\xbf\xf3f\x1a\
\xcd\xa2\x08B$(\xabyDYQH-\xdc\xf7\x17\xa6\xa0?\xe0>\x84\x82\x90\xa1E\x82\xfd\
\x84\x16\xad\\9?\xa1EI\x90\x14\x8c\xa4\xa8 \x8c\x08Y\x81\xb6\xd0\xd1\xd1\x19\
\xdf}\xe7\x9c\x16\xcf\x99\x1c\xad\x0b\x87{\xe0\xdc\xef\xbb\xe7\\\xae\x00\x94\
\xca\xd3\x85\x87W/\xae\xe6sQ\xef\xec\xd2f\\\x99|\\\xe7\x1f\xebQ\xe9\xf9\xf9[\
wn\xd6vw\xf6[_\xbf\x7f,.W*\x89\xb4\x8b\xdd\x92\x95\xb829Z?\x0e\xc77\x8a\xb5\
\xbd\xfd\xbdV\xf5\xc7\xe7\xe2r\xa5\x92\x00\xc8\xd1C\xa5\xf2t\xe1\xde\xa5s\
\xab\x82\xf7~\xab\xce\xc7\x95\xb7/\xeam\xf8\xca\xf5\xcb\xb5\xfdF\xab\xb5\xf0\
\xe1Kqy9\x83O\x08\x00J\xa5r\xe1\xda\x83\xdb5\xb3\xf4\xf4\xb7\xb9\xf9xkk\x8b\
\xbb\xf7o\xd7\xf6v\x9b\xcd\xa5O\xd5\xf8(\xdc\x11\x8c\x8d\x8d\xbd\x12\x91\x97\
\xee\x0e\x80\xbb\xd3\xdf\xdf\x9f\x03PU\xcc\x8c\x8d\x8d\ruw\xdc\x1dU\xa5\xd1h\
\xbc\x9e\x9a\x9a*\xe7\x0fE\xe3\xc5\'\x13\'\xbaq\x07u0s\xac\xa9\xb9\x9f;\x81\
\xa6\x82\x03\xdb\xef\x9e\x8e\x03\xe5\x08\xa0\xaf\xafO\xfa\xcf\x08\x91\x9c\
\x84Su~\xd5\x03\xeb\xf5@jBN \x02B\x08\x02Y\x8e\xbb\xd3\x9b\x87\x81\xb3B>\xfa\
\x0b\xb7\x12e};a71r"\xe4\xa2\x0c\x88DPU:\x82\x10\x02A3\xf0B\xaf \x92\xc1\xbf\
\x1b)n\x1c\xc2B\x84\x10\x89\x109\x1dA\x1e I\x12\x12\x03\x0eo.\x88So) \x888\
\x11`N\x96;\x98\x1c\x13\xa8*A\xb3Cj\xc6n0\xfa\n\x11A\x9d(\x02U@\x1cq\xc1\x0f\
\xdf\xa8K\x90\xa6)\x07\xea\xb8A3u\xd4\xb29O\xe5\x9c4H\x17\xdc\x0e3\xeb\x1ea\
\xef\xc0\t\x06\xcd\xe0\xa4\n\xea\x8e\xba\xe0\x92\xf5l~\x04\xc6\xbb\x05===l\
\xbf\x7f\xc3\xda\xda\x1a\x13++<\x1b\x1c$\x84\xc0\xd0\xd0\x10\x8bss\x0c\x0f\
\x0f3;;\xcb\xc8\xc8\x08333\xc4q\xdc\x19A\x00FGG}``\x00U\xfdo\x98Yg73\x16\x16\
\x16\xa8V\xab\x92\x07\xd8\xdc\xdcdqq\xb1S43\xdc\xfdD\xde\xfe\xca\xed\xbf\x03\
\xf0\x07L\xc5\x86\xbd\x8c~\xe9\x92\x00\x00\x00\x00IEND\xaeB`\x82\xe4\x13\x1c\
\x95' )

def getBitmap():
    return BitmapFromImage(getImage())

def getImage():
    stream = cStringIO.StringIO(getData())
    return ImageFromStream(stream)
