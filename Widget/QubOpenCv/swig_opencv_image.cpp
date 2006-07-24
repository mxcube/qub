#include "swig_opencv_image.h"

static swig_type_info *the_qtTools_IplImage_info = NULL;

swig_type_info* SWIG_IplImageInfo()
{
  if(!the_qtTools_IplImage_info)
    the_qtTools_IplImage_info = SWIG_TypeQuery("IplImage*");
  return the_qtTools_IplImage_info;
}
