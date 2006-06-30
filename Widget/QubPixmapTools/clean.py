#!/usr/bine/env python

import os
import os.path

dont_rm_files = ['QubPixmapTools.sip','QubPixmapTools_io.cpp','QubPixmapTools_io.h','QubPixmapToolsconfig.py.in','configure.py',
                 'clean.py']

for root,dirs,files in os.walk('.') :
    for file_name in files :
        if file_name not in dont_rm_files :
            os.remove(os.path.join(root,file_name))
    break
