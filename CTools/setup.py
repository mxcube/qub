import glob
import platform
from distutils.core import setup,Extension

if platform.system() == 'Linux' :
    extra_compile_args = ['-pthread','-msse2','-mfpmath=sse']
elif platform.system() == 'SunOS' :
    extra_compile_args = ['-mt']
else:
    extra_compile_args = []
    
polygone_module = Extension(name = "polygone",
                            sources = glob.glob('polygone/polygone*cpp'),
                            extra_compile_args = extra_compile_args,
                            include_dirs = ['polygone'])

dataresize_module = Extension(name = "datafuncs",
                              sources = glob.glob('datafuncs/datafuncs*cpp'),
                              extra_compile_args = extra_compile_args,
                              include_dirs = ['datafuncs'])

setup(name = "QubCTools",version = "1.0",
      description = "Some tools written in C for speed",
      ext_modules = [polygone_module,dataresize_module])

