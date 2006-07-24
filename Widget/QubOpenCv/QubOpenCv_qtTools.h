#include "qimage.h"
#include "opencv/cxcore.h"

class qtTools
{
public :
  static QImage* getQImageFromImageOpencv(const IplImage*);
  static IplImage* getImageOpencvFromQImage(const QImage*);
};

