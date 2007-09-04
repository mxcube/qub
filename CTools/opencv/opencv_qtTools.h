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

  static QImage getQImageFromImageOpencv(const IplImage*) throw(Exception);
  static IplImage* getImageOpencvFromQImage(const QImage*);
  static IplImage* convertI420Data2YUV(const char *data,int width,int height);
};

