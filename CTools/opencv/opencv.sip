%Import qt/qtmod.sip

%Module opencv 0

%Doc
<h1>Class qtTools</h1>
<p>
This class provide a transformation between Opencv image and QImage (Only in 8 bits for now)
</p>
%End

%MappedType sizedString 
{
%TypeHeaderCode
#include "opencv_bayer.h"
%End

%ConvertToTypeCode
int val;
%End

%ConvertFromTypeCode
 PyObject *anPyImage = PyString_FromStringAndSize(sipCpp->_data, sipCpp->_size);
 // Return the Python Image.
 return anPyImage;
%End
};



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
};

class bayer
{
%TypeHeaderCode
#include <opencv_bayer.h>
%End
public :
  enum CODE {BayerBG2BGR, BayerGB2BGR, BayerRG2BGR, BayerGR2BGR,
	     BayerBG2RGB, BayerGB2RGB, BayerRG2RGB, BayerGR2RGB};
  bayer(const char*,int,int);
  ~bayer();
  sizedString toRgb(bayer::CODE);
};
