#include "qimage.h"
#include "opencv/cxcore.h"


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
};

