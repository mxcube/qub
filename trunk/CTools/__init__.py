import os
import os.path

dirname = __path__[0]
platforms = []

try:
  platforms = os.environ["QUB_COMPAT_OS"].split()
except KeyError:
  cs_admin_path = '/csadmin/local/scripts/get_compat_os.share'
  if os.access(cs_admin_path,os.X_OK) :
    cmd = os.popen(cs_admin_path)
    platforms = cmd.read().split()
    cmd.close()
  else:
    raise ImportError('This module cannot be imported without get_compat_os.share, or define the QUB_COMPAT_OS environment variable.')

for plat in platforms:
    __path__.append(os.path.join(dirname,'lib',plat))
