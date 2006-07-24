#include <QubOpenCv_qtTools.h>

static inline void _copy_opencv2qimage_3channel(const IplImage *aSImage,
						QImage *aQImage)
{
  for(int line = 0;line < aSImage->height;++line)
    {
      char *aPt = aSImage->imageData + line * aSImage->widthStep;
      QRgb *aDestPt = (QRgb*)aQImage->scanLine(line);
      for(int column = 0;column < aSImage->width;++column,aPt += 3,++aDestPt)
	{
	  int r = aPt[2],g = aPt[1],b = aPt[0];
	  *aDestPt = qRgb(r,g,b);
	}
    }    
}

static inline void _copy_opencv2qimage_3channel_aplha(const IplImage *aSImage,
						      QImage *aQImage)
{
  for(int line = 0;line < aSImage->height;++line)
    {
      char *aPt = aSImage->imageData + line * aSImage->widthStep;
      QRgb *aDestPt = (QRgb*)aQImage->scanLine(line);
      for(int column = 0;column < aSImage->width;++column,aPt += 4,++aDestPt)
	{
	  int r = aPt[2],g = aPt[1],b = aPt[0],a = aPt[3];
	  *aDestPt = qRgba(r,g,b,a);
	}
    }    
}

QImage* qtTools::getQImageFromImageOpencv(const IplImage *aSImage)
{
  QImage *aQImage = NULL;
  if(aSImage && (aSImage->depth & IPL_DEPTH_8U))	// Only 8 bit Image
    {
      int depth = aSImage->nChannels == 1 ? 8 : 32;
      aQImage = new QImage(aSImage->width,aSImage->height,depth);
      if(aSImage->nChannels == 1)
	{
	  int lines;
	  char *aPt;
	  for(lines = 0,aPt = aSImage->imageData;
	      lines < aSImage->height;++lines,aPt += aSImage->widthStep)
	    memcpy(aQImage->scanLine(lines),aPt,aSImage->width);
	  aQImage->setNumColors(256);
	  for(int i = 0;i < 256;++i)
	    aQImage->setColor(i,qRgb(i,i,i));
	}
      else
	{
	  if(aSImage->nChannels == 3)
	    _copy_opencv2qimage_3channel(aSImage,aQImage);
	  else if(aSImage->nChannels == 4)
	    _copy_opencv2qimage_3channel_aplha(aSImage,aQImage);
	}
    }
  return aQImage;
}

static inline void _copy_qimage2opencv_3channel(const QImage *aQImage,
						IplImage *aIplImage)

{
  for(int line = 0;line < aIplImage->height;++line)
    {
      char *aPt = aIplImage->imageData + line * aIplImage->widthStep;
      QRgb *aRgbPt = (QRgb*)aQImage->scanLine(line);
      for(int column = 0;column < aIplImage->width;++column,aPt += 3,++aRgbPt)
	aPt[2] = qRed(*aRgbPt),aPt[1] = qGreen(*aRgbPt),aPt[0] = qBlue(*aRgbPt);
    }    
}

static inline void _copy_qimage2opencv_3channel_aplha(const QImage *aQImage,
						      IplImage *aIplImage)
						      
{
 for(int line = 0;line < aIplImage->height;++line)
    {
      char *aPt = aIplImage->imageData + line * aIplImage->widthStep;
      QRgb *aRgbPt = (QRgb*)aQImage->scanLine(line);
      for(int column = 0;column < aIplImage->width;++column,aPt += 4,++aRgbPt)
	aPt[2] = qRed(*aRgbPt),aPt[1] = qGreen(*aRgbPt),aPt[0] = qBlue(*aRgbPt),aPt[3] = qAlpha(*aRgbPt);
    }    
}

IplImage* qtTools::getImageOpencvFromQImage(const QImage *aQImage)
{
  IplImage *aIplImage = NULL;
  if(aQImage)
    {
      if(aQImage->depth() == 8)
	{
	  int lines;
	  char *aPt;
	  aIplImage = cvCreateImage(cvSize(aQImage->width(),aQImage->height()),
				    IPL_DEPTH_8U,1);
	  for(lines = 0,aPt = aIplImage->imageData;
	      lines < aIplImage->height;++lines,aPt += aIplImage->widthStep)
	    memcpy(aPt,aQImage->scanLine(lines),aIplImage->width);
	}
      else
	{
	  aIplImage = cvCreateImage(cvSize(aQImage->width(),aQImage->height()),
				    IPL_DEPTH_8U,aQImage->hasAlphaBuffer() ? 4 : 3);
	  if(aQImage->hasAlphaBuffer())
	    _copy_qimage2opencv_3channel_aplha(aQImage,aIplImage);
	  else
	    _copy_qimage2opencv_3channel(aQImage,aIplImage);
	}

    }
  return aIplImage;
}
