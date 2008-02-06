#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>

#include <iostream>

#include "qttools_mmap.h"


BgrImageMmap::BgrImageMmap(const char *aFilePath)
{
  _fd = open(aFilePath,O_RDWR);
  if(_fd < 0) 
    std::cerr << "BgrImageMmap : Can't open File "  << aFilePath << std::endl;
  else
    {
      _mappedSize = lseek(_fd,0,SEEK_END);
      lseek(_fd,0,SEEK_SET);
      _mmapMemoryPt = mmap(NULL,_mappedSize,
			   PROT_WRITE|PROT_READ,MAP_SHARED,_fd,0);
      _headerPt = (Header*)_mmapMemoryPt;
  
      _headerPt->copy_request = 1;
      msync(_mmapMemoryPt,sizeof(Header),MS_ASYNC);
    }
}

BgrImageMmap::~BgrImageMmap()
{
  if(_fd > -1)
    {
      munmap(_mmapMemoryPt,_mappedSize);
      close(_fd);
    }
}

int BgrImageMmap::getImageCount()
{
  int imageCount = -1;
  if(_fd >= -1)
    {
      imageCount = _headerPt->imageCount;
      if(!_headerPt->image_available && !_headerPt->copy_request)
	{
	  _headerPt->copy_request = 1;
	}
      _headerPt->image_available = 0;
      msync(_mmapMemoryPt,sizeof(Header),MS_ASYNC);
    }
  return imageCount;
}

QImage BgrImageMmap::getNewImage()
{
  uchar *endImagePt = ((uchar*)_mmapMemoryPt + sizeof(Header)) + 
    (_headerPt->width * _headerPt->height * 3);
  uchar *endFilePt = ((uchar*)_mmapMemoryPt + sizeof(Header)) + _mappedSize;
  if(endImagePt > endFilePt) endImagePt = endFilePt;
  
  QImage aQImage(_headerPt->width,_headerPt->height,32);
  uchar *aDestPt = aQImage.scanLine(0);
  uchar * imagePt = ((uchar*)_mmapMemoryPt + sizeof(Header));
  while(imagePt < endImagePt)
    {
//       *aDestPt = *imagePt;++imagePt,++aDestPt; // Blue
//       *aDestPt = *imagePt;++imagePt,++aDestPt; // Green
//       *aDestPt = *imagePt;++imagePt,++aDestPt; // Red
//       ++aDestPt;
      aDestPt[2] = *imagePt;++imagePt;
      aDestPt[1] = *imagePt;++imagePt;
      aDestPt[0] = *imagePt;++imagePt;
      aDestPt += 4;
    }
  _headerPt->copy_request = 1;
  msync(_mmapMemoryPt,sizeof(Header),MS_ASYNC);
  return aQImage;
}
