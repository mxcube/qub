#!/usr/bine/env python

import os
import os.path

dont_rm_files = ['QubOpenCv.sip','QubOpenCv_qtTools.cpp','QubOpenCv_qtTools.h',
                 'QubOpenCvconfig.py.in','configure.py','swigpyrun.h',
                 'swig_opencv_image.h','swig_opencv_image.cpp',
                 'QubOpenCv_bayer.cpp','QubOpenCv_bayer.h',
                 'clean.py']

for root,dirs,files in os.walk('.') :
    for file_name in files :
        if file_name not in dont_rm_files :
            os.remove(os.path.join(root,file_name))
    break
