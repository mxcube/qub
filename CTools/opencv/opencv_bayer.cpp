#include <opencv_bayer.h>

bayer::bayer(const char *aData,int rows, int cols) :
   _data(aData),
   _rows(rows),
   _cols(cols),
   _result(NULL)
{
}

bayer::~bayer()
{
  if(_result)
      cvReleaseImage(&_result);
}

sizedString bayer::toRgb(bayer::CODE aCode)
{
  int acvCode = (aCode == BayerBG2BGR ? CV_BayerBG2BGR :
		 (aCode == BayerGB2BGR ? CV_BayerGB2BGR :
		  (aCode == BayerRG2BGR ? CV_BayerRG2BGR :
		   (aCode == BayerGR2BGR ? CV_BayerGR2BGR :
		    (aCode == BayerBG2RGB ? CV_BayerBG2RGB :
		     (aCode == BayerGB2RGB ? CV_BayerGB2RGB : 
		      (aCode == BayerRG2RGB ? CV_BayerRG2RGB : CV_BayerGR2RGB)))))));
  
  IplImage* aSrc = cvCreateImage(cvSize(_cols, _rows), IPL_DEPTH_8U, 1);
  cvSetData(aSrc, const_cast<char *>(_data), _cols);
  
  if(_result)
    cvReleaseImage(&_result);
  
  _result = cvCreateImage(cvSize(_cols,_rows), IPL_DEPTH_8U,3);
  cvCvtColor(aSrc, _result, acvCode);

  return sizedString(_result->imageData, _cols*_rows*3); 
  //return (const char*)_result->imageData;
}
