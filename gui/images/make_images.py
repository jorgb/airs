#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os, os.path
import wxversion
wxversion.select('2.8')
import wx

import os.path, glob
import wx.tools.img2py as i2p

image_exts = ['*.png', '*.gif', '*.bmp']
images = []
for ext in image_exts:
    images.extend(glob.glob(ext))

for name in images:
    root, ext = os.path.splitext(name)
    
    src_f = os.stat(name).st_mtime
    make_dst = True
    dst_name = root + '.py'
    if os.path.isfile(dst_name):
        dst_f = os.stat(dst_name).st_mtime
        make_dst = src_f > dst_f       # make when image is newer then python file
            
    if make_dst:
        print 'Converting', name, ' to ', root + '.py'
        i2p.img2py(name, root + '.py')
