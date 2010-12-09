import glob
import platform
from distutils.core import setup,Extension
import sipdistutils
import numpy
import os

QT3=True
if QT3:
    print "***** doing setup.py for Qt3 *****"
    import pyqtconfig
else:
    print "***** doing setup.py for Qt4 *****"
    import PyQt4.pyqtconfig as pyqtconfig

# Get the PyQt configuration information.
config = pyqtconfig.Configuration()
if QT3:
  sip_flags = config.pyqt_qt_sip_flags.split()
  qt_inc_dir = config.qt_inc_dir
  qt_lib = config.qt_lib
else:
  sip_flags = config.pyqt_sip_flags

# configure sip build_ext
class my_own_build_ext(sipdistutils.build_ext):
   def __init__(self, *args, **kwargs):
     sipdistutils.build_ext.__init__(self, *args, **kwargs) 
   def finalize_options(self):
     sipdistutils.build_ext.finalize_options(self)
     self.sip_opts = sip_flags
   def _sip_sipfiles_dir(self):
     config=pyqtconfig.Configuration()
     return config.pyqt_sip_dir

if platform.system() == 'Linux' :
    try:
        if platform.architecture()[0] == '64bit' :
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

pixmaptools_module = Extension(name = "pixmaptools",
                               sources = ["pixmaptools/%s.sip" % (QT3 and "pixmaptools_qt3" or "pixmaptools_qt4")]+glob.glob('pixmaptools/pixmaptools_*.cpp'),
                               extra_compile_args = extra_compile_args,
                               extra_link_args = extra_link_args+['-l'+qt_lib],
                               include_dirs = ['pixmaptools', numpy.get_include(), qt_inc_dir]) 
                               

setup(name = "QubCTools",version = "1.0",
      description = "Some tools written in C for speed",
      ext_modules = [polygone_module,dataresize_module,sps_module,mar345_module,pixmaptools_module],
      cmdclass={'build_ext': my_own_build_ext})

