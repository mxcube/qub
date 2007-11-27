#include "qimage.h"

class QubImage : public QImage
{
public:
  QubImage () : QImage() {}
  QubImage(const QImage &anImage) : QImage(anImage) {}
  QubImage(const QubImage &anImage) : QImage(anImage) {}
  void highlightImage(int ox,int oy,int ex,int ey);
  void unhighlightImage(int ox,int oy,int ex,int ey);

  void setGray(int ox,int oy,int ex,int ey);
  void erase(int ox,int oy,int ex,int ey);
  QubImage copy () const;
  QubImage copy ( int x, int y, int w, int h, int conversion_flags = 0 ) const;
  QubImage copy ( const QRect & r ) const;
};
