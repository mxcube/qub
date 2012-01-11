#include "qimage.h"

class QubImage : public QImage
{
public:
  enum rawType {RGB555,RGB565};

  QubImage () : QImage() {}
  QubImage(const QImage &anImage) : QImage(anImage) {}
  QubImage(const QubImage &anImage) : QImage(anImage) {}
  explicit QubImage(rawType aType,int width,int height,const char *rawData);

  void highlightImage(int ox,int oy,int ex,int ey);
  void unhighlightImage(int ox,int oy,int ex,int ey);

  void setGray(int ox,int oy,int ex,int ey);
  void erase(int ox,int oy,int ex,int ey);
  QubImage copy () const;
  QubImage copy ( int x, int y, int w, int h, int conversion_flags = 0 ) const;
  QubImage copy ( const QRect & r ) const;
};
