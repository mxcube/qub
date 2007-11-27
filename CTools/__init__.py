import os
import os.path

try:
  __path__ = os.environ["QUB_COMPAT_OS"].split()
except KeyError:
  cs_admin_path = '/csadmin/local/scripts/get_compat_os.share'
  if os.access(cs_admin_path,os.X_OK) :
    dirname = __path__[0]
    cmd = os.popen(cs_admin_path)
    for platform in cmd.read().split() :
        __path__.append(os.path.join(dirname,'lib',platform))
    cmd.close()
  else:
    raise ImportError('This module cannot be imported without get_compat_os.share, or define the QUB_COMPAT_OS environment variable.')
