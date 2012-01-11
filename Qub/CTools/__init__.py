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
    __path__.append(os.path.join(dirname,'lib'))

for plat in platforms:
    __path__.append(os.path.join(dirname,'lib',plat))

