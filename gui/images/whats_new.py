#----------------------------------------------------------------------
# This file was generated by D:\personal\src\airs\gui\images\make_images.py
#
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib


def getData():
    return zlib.decompress(
'x\xda\x01\xf5\x02\n\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x02\xacIDAT8\x8d\xa5\x92?l[e\x14\xc5\x7f\x9f\
\xdf{v\x9e\x1d7y\x89R\xd2&\x8d\xd0+m\xa0t\x817T\x0c\x1d\x10\x8f\x05\t\xb6dB\
\xb09R\x19\x90\xba4\x08U]Za\x18X*Uj\xd9[\x89L\xcc\xf5\x82P\x11C\xdc\x8a\x7fE\
\x0c\xb5\x94\x14\x91\xc6!}qm\xc7\xcf\xcf\xdfw?\x86\xc8\xc5\xb4l\x9c\xe9^\xdd\
s\xae\xee=:\xf0?\xa1F\x1b\xfb\x15\x91X\xaa\xd6\x12cXv\xcf\xb1\x06\xd0\xbdJ\
\x05Q\xd7\x8dP\x13kW&\xcf\xd3\x18jr#\xe2\x8a\xf8\x87\xd7\xd5\xfc[q.|\x0f\x83\
\xaa<\xdd,\xaa2\xb6\xf8\x0e\x85#\xaf\xc7br\xeb\xbb_8K\xc3\x91;,\xb4\xd0\xc8\
\xa91(\xce\xa2\xdc1\xacw(\xee}\xd9\n5\x84\xaat$\xca\xb9>\xce\xf84"`\xc5<\x7f\
\x81\xb7B\xcd\xb46WM\xf3\'@p\xa6_A+uA\xacZr&\x8e\x81\x15\xd2\xed\x06VX\x9d\
\xf9\x84\xfa\x7fz\x00\xb0\x7fU\xddvg_\x8b\xdd\x99\x97\xe9\xdc\xbd\x95\x14\
\x16\xce\x04\xf9\xc99z\x7f\xfeN\xf7\xe1\xaf7f>\xb5+\xa3|7\xbbF\x04\x90?w\xb0\
5s\xec\xb2yx\xef\x81;\xf5R0\xfe\xea\xbb\x81R\xa0\xbb\t\xed\xcd\xfb\xf5\xd4\
\xb1\xabC\xe1\xc6E/b\x00\xaa\x7fM\xdd\xc6?\x1c\x9bN\x13kH\x8c\xa5n\x85\xa0\
\xb4\x18G\x8e\xe7\x82\x08:M\xd9\xfd\xe5\xbb\xba\x08\x89h\x15\x8a%t\x8b\x87\
\xd8\xdfk\xd7\\+\xe0\xcd\xbdA\xbe<\x87t\x1e\x05\x92\xf5b\xc4\xe2\xf8>\x0c\
\xba \x1a\xd7\xf7\x99:\xfdf$\x83\x14\xa7\xe0\xe3\xe6\x0b\xf4\x1e\xef\xd0\xda\
\xb9\x8bk\x0c\xe8\xfb\xdf`\x05\xc4\xaa\xba\x11\x9bX\x03\xe5\x93gc\xcf\x1f\
\x03,\x83n\x87\xed\x1f\xbf\xaf\x8b&1V\x85\xa2U8\x18\xc0 S\xb8\xa5\x8f\xed\
\xdb#Qb\xef3\x82Lr\x0f\xdc\xd2\x14\xa6\xff\x04\xc7s\xb1\x92!\x1a\x10Y\x0e\
\xab$\xa3&\xe6x\x06\x99\xa8\xaf\x8b\xf3\xa7\x03\xdd\xef\xf1h\xfd\xdbFg\xe7/\
\xf2\xa5q\xca\xc7ND}\xedT\x9f\xe5;\xa3M\xf3\x8a\xaa\x16f\x17?(/\x9c\xa2\xbd\
\xf1\x1b\xe9\x93\xc7\xab\xdd\xe6\xf6\x96S(F\x13G_ Km\xf4\xfe\xf1Nz}]\xee<wA\
\xf3\xb2\xb3\x94\x9f~\xf1By\xe1\x14\xa6\xd7\xa5\xfdG#a kbY\xdb\xdb\xda\x06+L\
/\x1c%_\x9c\xa8\xfe\xf0\xa1\x17=\xcd\xc1\xb00\x06\xf6\xb76\x13\xc7\x0f\x02\
\xddO\xd1b??\xf8\xd7\xd4~\xfeh\xb7>9\xdf\x8bZ[\xbb\xb4v\xda\x89\xd1*\x84\x83\
\xdc\xfc+\x89\x1b\x97\x08\xd1NU\xc4\x06\x99\xf5V\x16\xab\xfd\x06\xc0\xbdJ~\
\xa9\xafm\xc5d\xaa&\x92\xdd8{\xf3\x1f#\xff\x06\xae\x01GxF\x11Os\x00\x00\x00\
\x00IEND\xaeB`\x82\xdcDd\x8f' )

def getBitmap():
    return BitmapFromImage(getImage())

def getImage():
    stream = cStringIO.StringIO(getData())
    return ImageFromStream(stream)

