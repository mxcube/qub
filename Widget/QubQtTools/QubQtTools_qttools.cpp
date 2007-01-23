
#include "QubQtTools_qttools.h"


bool qttools::get_qt_resolve_symlinks() 
{
  extern bool qt_resolve_symlinks;
  return qt_resolve_symlinks;
}

void qttools::set_qt_resolve_symlinks(bool aFlag) 
{
  extern bool qt_resolve_symlinks;
  qt_resolve_symlinks = aFlag;
}
