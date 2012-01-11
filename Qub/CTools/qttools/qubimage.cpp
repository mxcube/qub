#include <iostream>
#include "qubimage.h"

#define FOR_EACH_PIXEL \
for(int y = oy;y < ey;++y) \
  { \
    for(int x = ox;x < ex;++x) \
      { \
	int rgb = image.pixel(x,y); \
	int alpha = qAlpha(rgb); \
	if(alpha) \
	  { \
	    DO_ONE_PIXEL; \
	  } \
      } \
  }

inline void _pixelFactor(QImage & image,int ox,int oy,int ex,int ey,double factor) 
{
#ifdef DO_ONE_PIXEL
#undef DO_ONE_PIXEL
#endif
#define DO_ONE_PIXEL \
  int red,green,blue; \
  red = int(qRed(rgb) * factor); \
  green = int(qGreen(rgb) * factor); \
  blue = int(qBlue(rgb) * factor); \
  image.setPixel(x,y,qRgba(red,green,blue,alpha));
FOR_EACH_PIXEL;
}

void QubImage::highlightImage(int ox,int oy,int ex,int ey)
{
  _pixelFactor(*this,ox,oy,ex,ey,1.25);
}

void QubImage::unhighlightImage(int ox,int oy,int ex,int ey)
{
  _pixelFactor(*this,ox,oy,ex,ey,0.8);
}

void QubImage::setGray(int ox,int oy,int ex,int ey)
{
#ifdef DO_ONE_PIXEL
#undef DO_ONE_PIXEL
#endif
#define DO_ONE_PIXEL  \
  int gray; \
  gray = int(qRed(rgb) * 0.299) + int(qGreen(rgb) * 0.587) + int(qBlue(rgb) * 0.114); \
  setPixel(x,y,qRgba(gray,gray,gray,alpha));
  
  QImage &image = *this;
FOR_EACH_PIXEL; 
}
void QubImage::erase(int ox,int oy,int ex,int ey)
{
#ifdef DO_ONE_PIXEL
#undef DO_ONE_PIXEL
#endif
#define DO_ONE_PIXEL setPixel(x,y,qRgba(0,0,0,0));

QImage &image = *this;
FOR_EACH_PIXEL;
}

QubImage QubImage::copy() const 
{return QubImage(this->QImage::copy());}

QubImage QubImage::copy( int x, int y, int w, int h, int conversion_flags) const
{return QubImage(this->QImage::copy(x,y,w,h,conversion_flags));}

QubImage QubImage::copy( const QRect & r ) const
{return QubImage(this->QImage::copy(r));}



static inline void _copy_from_rgb555(QubImage &anImage,
				     int width,int height,
				     const char *rawDataPt)
{
  unsigned int *aDestPt = (unsigned int*) anImage.scanLine(0);
  const unsigned int *aSrcPt = (const unsigned int*)rawDataPt;
  for(int nbIter = width * height / 2;nbIter;--nbIter,++aSrcPt)
    {
      *aDestPt = 
	((0x7c000000 & *aSrcPt) >> 7) |
	((0x03E00000 & *aSrcPt) >> 10) |
	((0x001f0000 & *aSrcPt) >> 13);
      ++aDestPt;

      *aDestPt = 
	((0x00007c00 & *aSrcPt) << 9) |
	((0x000003E0 & *aSrcPt) << 6) |
	((0x0000001f & *aSrcPt) << 3);
      ++aDestPt;
    }
}

static inline void _copy_from_rgb565(QubImage &anImage,
				     int width,int height,
				     const char *rawDataPt)
{
  unsigned int *aDestPt = (unsigned int*) anImage.scanLine(0);
  const unsigned int *aSrcPt = (const unsigned int*)rawDataPt;
  for(int nbIter = width * height / 2;nbIter;--nbIter,++aSrcPt)
    {
      *aDestPt = 
	((0xf8000000 & *aSrcPt) >> 9) |
	((0x07E00000 & *aSrcPt) >> 11) |
	((0x001f0000 & *aSrcPt) >> 14);
      ++aDestPt;

      *aDestPt = 
	((0x0000f800 & *aSrcPt) << 7) |
	((0x000007E0 & *aSrcPt) << 5) |
	((0x0000001f & *aSrcPt) << 2);
      ++aDestPt;
    }
}

QubImage::QubImage(QubImage::rawType aType,
		   int width,int height,
		   const char *rawDataPt) :
  QImage(width,height,32)
{
  switch(aType)
    {
    case RGB555: _copy_from_rgb555(*this,width,height,rawDataPt);break;
    case RGB565: _copy_from_rgb565(*this,width,height,rawDataPt);break;
    default:
      std::cerr << "QubImage: RawType not yet managed" << std::endl;
    }
}
