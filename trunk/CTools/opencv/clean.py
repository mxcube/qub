#!/usr/bine/env python

import os
import os.path

dont_rm_files = ['opencv.sip','opencv_qtTools.cpp','opencv_qtTools.h',
                 'opencvconfig.py.in','configure.py','swigpyrun.h',
                 'swig_opencv_image.h','swig_opencv_image.cpp',
                 'clean.py']

for root,dirs,files in os.walk('.') :
    for file_name in files :
        if file_name not in dont_rm_files :
            os.remove(os.path.join(root,file_name))
    break
