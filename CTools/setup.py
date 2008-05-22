import glob
import platform
from distutils.core import setup,Extension
import numpy
import os

if platform.system() == 'Linux' :
    try:
        if os.environ['OSTYPE'] == 'suse72':
            extra_compile_args = ['-pthread']
        else:
            extra_compile_args = ['-pthread','-march=pentium4']
    except KeyError:
        extra_compile_args = ['-pthread','-march=pentium4']
    extra_link_args = ['-pthread']
elif platform.system() == 'SunOS' :
    extra_compile_args = ['-pthreads']
    extra_link_args = ['-pthreads']#['-Wl,-mt,-lpthread']
else:
    extra_compile_args = []
    
polygone_module = Extension(name = "polygone",
                            sources = glob.glob('polygone/polygone*cpp'),
                            extra_compile_args = extra_compile_args,
			    extra_link_args = extra_link_args,
                            include_dirs = ['polygone'])

dataresize_module = Extension(name = "datafuncs",
                              sources = glob.glob('datafuncs/datafuncs*cpp'),
                              extra_compile_args = extra_compile_args,
			      extra_link_args = extra_link_args,
                              include_dirs = ['datafuncs',numpy.get_include()])
sps_module = Extension(name = "sps",
                              sources = glob.glob('sps/sps*c'),
                              extra_compile_args = extra_compile_args,
			      extra_link_args = extra_link_args,
                              include_dirs = ['sps',numpy.get_include()])

mar345_module = Extension(name = "mar345",
                          sources = glob.glob('mar345/mar345*c'),
                          extra_compile_args = extra_compile_args,
                          extra_link_args = extra_link_args,
                          include_dirs = ['mar345',numpy.get_include()])

setup(name = "QubCTools",version = "1.0",
      description = "Some tools written in C for speed",
      ext_modules = [polygone_module,dataresize_module,sps_module,mar345_module])

