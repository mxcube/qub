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
  qt_lib_dir = config.qt_lib_dir
else:
  sip_flags = config.pyqt_sip_flags

# configure sip build_ext
class my_own_build_ext(sipdistutils.build_ext):
   def __init__(self, *args, **kwargs):
     sipdistutils.build_ext.__init__(self, *args, **kwargs) 
   def _sip_sipfiles_dir(self):
     config=pyqtconfig.Configuration()
     return config.pyqt_sip_dir
   def _sip_compile(self, sip_bin, source, sbf):
     parameters = sip_flags[:]
     parameters.extend(["-c", self.build_temp, "-b", sbf, "-I", pyqtconfig.Configuration().pyqt_sip_dir, source])
     cmdline = [sip_bin]
     cmdline.extend(parameters)
     self.spawn(cmdline)

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
    
polygone_module = Extension(name = "Qub.CTools/polygone",
                            sources = glob.glob('Qub/CTools/polygone/polygone*cpp'),
                            extra_compile_args = extra_compile_args,
			    extra_link_args = extra_link_args,
                            include_dirs = ['Qub/CTools/polygone'])

dataresize_module = Extension(name = "Qub.CTools/datafuncs",
                              sources = glob.glob('Qub/CTools/datafuncs/datafuncs*cpp'),
                              extra_compile_args = extra_compile_args,
			      extra_link_args = extra_link_args,
                              include_dirs = ['Qub/CTools/datafuncs',numpy.get_include()])

mar345_module = Extension(name = "Qub.CTools/mar345",
                          sources = glob.glob('Qub/CTools/mar345/mar345*c'),
                          extra_compile_args = extra_compile_args,
                          extra_link_args = extra_link_args,
                          include_dirs = ['Qub/CTools/mar345',numpy.get_include()])

qttools_module = Extension(name = "Qub.CTools/qttools",
                           sources = ["Qub/CTools/qttools/%s.sip" % (QT3 and "qttools_qt3" or "qttools_qt4")]+glob.glob('Qub/CTools/qttools/*cpp'),
                           extra_compile_args = extra_compile_args,
                           extra_link_args = extra_link_args+['-l'+qt_lib, '-lXext', '-lX11'],
                           include_dirs = ['Qub/CTools/qttools',numpy.get_include(), qt_inc_dir],
                           library_dirs = [qt_lib_dir])


pixmaptools_module = Extension(name = "Qub.CTools/pixmaptools",
                               sources = ["Qub/CTools/pixmaptools/%s.sip" % (QT3 and "pixmaptools_qt3" or "pixmaptools_qt4")]+glob.glob('Qub/CTools/pixmaptools/pixmaptools_*.cpp'),
                               extra_compile_args = extra_compile_args,
                               extra_link_args = extra_link_args+['-l'+qt_lib],
                               include_dirs = ['Qub/CTools/pixmaptools', numpy.get_include(), qt_inc_dir],
                               library_dirs = [qt_lib_dir]) 
                               
opencv_module = Extension(name = "Qub.CTools/opencv",
                               sources = ["Qub/CTools/opencv/%s.sip" % (QT3 and "opencv_qt3" or "opencv_qt4")]+glob.glob('Qub/CTools/opencv/*.cpp'),
                               extra_compile_args = extra_compile_args,
                               extra_link_args = extra_link_args+['-l'+qt_lib, '-lcv'],
                               include_dirs = ['Qub/CTools/opencv', numpy.get_include(), qt_inc_dir],
                               library_dirs = [qt_lib_dir]) 
                               

setup(name = "Qub",version = "1.0",
      description = "Qub is a library providing data display tools for PyQt apps", 
      author="Sebastien Petitdemange, BCU(Bliss), ESRF",
      packages = ["Qub", "Qub.CTools", "Qub.Data", "Qub.Data.Plug", "Qub.Data.Source", "Qub.Data.StreamIO", "Qub.Data.Scale", "Qub.Data.Class", "Qub.Icons", "Qub.Objects", "Qub.Objects.Mosaic", "Qub.Plugins", "Qub.Print", "Qub.Tools", "Qub.Widget", "Qub.Widget.DataSource", "Qub.Widget.Graph"],
      package_data = {"Qub.Icons":["IconsLibrary/*"], "Qub.Widget":["*.ui"]},
      ext_modules=[polygone_module,dataresize_module,mar345_module,pixmaptools_module, qttools_module,opencv_module],
      cmdclass={'build_ext': my_own_build_ext})

