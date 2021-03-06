#!/usr/bine/env python

import os
import os.path

dont_rm_files = ['qttools.sip',
                 'qttools_qttools.cpp','qttools_qttools.h',
                 'qtxembed.cpp','qtxembed.h',
                 'qubimage.h','qubimage.cpp',
                 'qttools_mmap.cpp','qttools_mmap.h',
                 'qttoolsconfig.py.in','configure.py',
                 'clean.py']

for root,dirs,files in os.walk('.') :
    for file_name in files :
        if file_name not in dont_rm_files :
            os.remove(os.path.join(root,file_name))
    break
