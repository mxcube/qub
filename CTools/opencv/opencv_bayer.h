#ifndef __BAYER__
#define __BAYER__
#include "opencv/cv.h"
#include "opencv/cxtypes.h"

typedef struct sizedString {
    sizedString(char *data, int size) : _data(data),
      _size(size)
    {}

    char *_data;
    int _size;
};


class bayer
{
public:
  enum CODE {BayerBG2BGR, BayerGB2BGR, BayerRG2BGR, BayerGR2BGR,
	     BayerBG2RGB, BayerGB2RGB, BayerRG2RGB, BayerGR2RGB};
  bayer(const char *aData,int rows, int cols);
  ~bayer();
  sizedString toRgb(bayer::CODE aCode);
private:
  const char *_data;
  int _rows,_cols;
  IplImage* _result;
};

#endif
