#include "swig_opencv_image.h"

class Init
{
public :
  Init()
  {
    the_qtTools_IplImage_info = SWIG_TypeQuery("IplImage*");
  }
  swig_type_info* getIplImage_info() {return the_qtTools_IplImage_info;}
private:
  swig_type_info *the_qtTools_IplImage_info;
};

static Init theInit;

swig_type_info* SWIG_IplImageInfo()
{
  return theInit.getIplImage_info();
}
