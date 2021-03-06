import os
import sipconfig
import pyqtconfig

# The name of the SIP build file generated by SIP and used by the build
# system.
build_file = "qttools.sbf"

# Get the PyQt configuration information.
config = pyqtconfig.Configuration()

# Get the extra SIP flags needed by the imported qt module.  Note that
# this normally only includes those flags (-x and -t) that relate to SIP's
# versioning system.
qt_sip_flags = config.pyqt_qt_sip_flags

# Run SIP to generate the code.  Note that we tell SIP where to find the qt
# module's specification files using the -I flag.
cmd = " ".join([config.sip_bin, "-c", '.', "-b", build_file, "-I", config.pyqt_sip_dir, qt_sip_flags,"qttools.sip"])
print cmd
os.system(cmd)

#MOC
if os.system(" ".join(['moc','-o','moc_qtxembed.cpp','qtxembed.h'])) :
    print 'Moc failed on file qtxembed.h'

compile_file = ['qttools_qttools.cpp','moc_qtxembed.cpp',
                'qtxembed.cpp','qubimage.cpp','qttools_mmap.cpp']

#little HACK for adding source
bfile = file(build_file)
whole_line = ''
for line in bfile :
    if 'sources' in line :
        begin,end = line.split('=')
        line = '%s = %s%s' % (begin,' '.join(compile_file),end)
    whole_line += line
bfile.close()
bfile = file(build_file,'w')
bfile.write(whole_line)
bfile.close()

# We are going to install the SIP specification file for this module and
# its configuration module.
installs = []

installs.append(["qttools.sip", os.path.join(config.default_sip_dir, "qttools")])

installs.append(["qttoolsconfig.py", config.default_mod_dir])

# Create the Makefile.  The QtModuleMakefile class provided by the
# pyqtconfig module takes care of all the extra preprocessor, compiler and
# linker flags needed by the Qt library.
makefile = pyqtconfig.QtModuleMakefile(
    configuration=config,
    build_file=build_file,
    installs=installs
  )

# Add the library we are wrapping.  The name doesn't include any platform
# specific prefixes or extensions (e.g. the "lib" prefix on UNIX, or the
# ".dll" extension on Windows).
# None (for me)

# Generate the Makefile itself.
makefile.generate()

# Now we create the configuration module.  This is done by merging a Python
# dictionary (whose values are normally determined dynamically) with a
# (static) template.
content = {
    # Publish where the SIP specifications for this module will be
    # installed.
    "qttools_sip_dir":    config.default_sip_dir,

    # Publish the set of SIP flags needed by this module.  As these are the
    # same flags needed by the qt module we could leave it out, but this
    # allows us to change the flags at a later date without breaking
    # scripts that import the configuration module.
    "qttools_sip_flags":  qt_sip_flags
}

# This creates the qttoolsconfig.py module from the qttoolsconfig.py.in
# template and the dictionary.
sipconfig.create_config_module("qttoolsconfig.py", "qttoolsconfig.py.in", content)
