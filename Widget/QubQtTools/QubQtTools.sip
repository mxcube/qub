

%Import qt/qtmod.sip


%Module QubQtTools 0

%Doc
<h1>Class qttools</h1>
<p>
This class is use to access to variable and fonction which is not wrap in qt module
</p>
%End

class qttools
{

%TypeHeaderCode
#include <QubQtTools_qttools.h>
%End

public:
	static bool get_qt_resolve_symlinks();
	static void set_qt_resolve_symlinks(bool);
};

