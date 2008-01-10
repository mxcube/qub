#!/usr/bine/env python

import os
import os.path

dont_rm_files = ['clean.py',
                 'configure.py',
                 'qwttoolsconfig.py.in',
                 'qwttools.sip',
                 'qwttools_scale.cpp',
                 'qwttools_scale.h']

for root,dirs,files in os.walk('.') :
    for file_name in files :
        if file_name not in dont_rm_files :
            os.remove(os.path.join(root,file_name))
    break
