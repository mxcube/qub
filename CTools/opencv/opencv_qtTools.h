#include "qimage.h"
#include "opencv/cv.h"

class qtTools
{
public :
  struct Exception
  {
    Exception(const char*);
    char _Message[512];
  };

  static QImage getQImageFromImageOpencv(const CvMat*) throw(Exception);
  static CvMat* getImageOpencvFromQImage(const QImage*);
  static QImage convertI420Data2YUV(const char *data,int width,int height);
};

