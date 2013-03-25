

%Import qt/qtmod.sip


%Module qttools 0

%Doc
<h1>Class qttools</h1>
<p>
This class is use to access to variable and fonction which is not wrap in qt module
</p>
%End

class qttools
{

%TypeHeaderCode
#include <qttools_qttools.h>
%End

public:
	static bool get_qt_resolve_symlinks();
	static void set_qt_resolve_symlinks(bool);
};

class QubImage :  QImage
{
%TypeHeaderCode
#include <qubimage.h>
%End
 public:
  enum rawType {RGB555,RGB565};

  QubImage();
  QubImage(const QImage &);
  QubImage(const QubImage &);
  explicit QubImage(rawType,int ,int ,const char *);

  void highlightImage(int ,int ,int ,int );
  void unhighlightImage(int ,int ,int ,int );
  void erase(int,int,int,int);
  void setGray(int,int,int,int);

  QubImage copy () const;
  QubImage copy ( int, int , int, int , int = 0 ) const;
  QubImage copy ( const QRect & r ) const;
};

class BgrImageMmap
{
%TypeHeaderCode
#include "qttools_mmap.h"
%End
public:
  BgrImageMmap(const char *aFilePath);
  ~BgrImageMmap();
  int getImageCount();
  QImage getNewImage();
};
