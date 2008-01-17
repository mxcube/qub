#include <qimage.h>

class BgrImageMmap
{
public:
  BgrImageMmap(const char *aFilePath);
  ~BgrImageMmap();
  int getImageCount();
  QImage getNewImage();

private:
  int   _fd;
  struct Header
  {
    int imageCount;
    int width;
    int height;
    int copy_request;
    int image_available;
    int spare;
  };
  Header *_headerPt;
  void *_mmapMemoryPt;
  int _mappedSize;
};
