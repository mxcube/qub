%Import qt/qtmod.sip

%Module opencv 0

%Doc
<h1>Class qtTools</h1>
<p>
This class provide a transformation between Opencv image and QImage (Only in 8 bits for now)
</p>
%End

%MappedType IplImage
{
%TypeHeaderCode
// Include the library interface to the type being mapped.
#include <opencv/cxcore.h>
#include "swig_opencv_image.h"
%End

%ConvertToTypeCode
    // See if we are just being asked to check the type of the Python
    // object.
    if (sipIsErr == NULL)
      {
	IplImage *aBuffer;
	return SWIG_ConvertPtr(sipPy,(void **)&aBuffer,SWIG_IplImageInfo(), 0) != -1;
      }
  
  IplImage *anImage;
  SWIG_ConvertPtr(sipPy,(void **)&anImage,SWIG_IplImageInfo(), 0);
  
  // Return the instance on the heap.
  *sipCppPtrV = anImage;
  
  // Apply the normal transfer.
  //  return sipGetState(sipTransferObj);
  return 0;
%End

%ConvertFromTypeCode
   PyObject *anPyImage = SWIG_NewPointerObj(sipCpp,SWIG_IplImageInfo(),1);
  // Return the Python Image.
  return anPyImage;
%End
};

class qtTools
{
%TypeHeaderCode
#include <opencv_qtTools.h>
%End

public :
  static QImage getQImageFromImageOpencv(const IplImage*);
  static IplImage* getImageOpencvFromQImage(const QImage*);
  static IplImage* convertI420Data2YUV(const char *data,int width,int height);
};
