import glob
from distutils.core import setup,Extension
polygone_module = Extension(name = "polygone",
                            sources = glob.glob('polygone/polygone*cpp'),
                            include_dirs = ['polygone'])

dataresize_module = Extension(name = "datafuncs",
                              sources = glob.glob('datafuncs/datafuncs*cpp'),
                              extra_compile_args = ['-msse2','-mfpmath=sse'],
                              include_dirs = ['datafuncs'])

setup(name = "QubCTools",version = "1.0",
      description = "Some tools written in C for speed",
      ext_modules = [polygone_module,dataresize_module])

