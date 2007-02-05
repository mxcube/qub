import glob
from distutils.core import setup,Extension
polygone_module = Extension(name = "polygone",
                            sources = glob.glob('polygone/polygone*cpp'),
                            include_dirs = ['polygone'])

setup(name = "QubCTools",version = "1.0",
      description = "Some tools written in C for speed",
      ext_modules = [polygone_module])

