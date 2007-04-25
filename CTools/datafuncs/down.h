#include <math.h>
/* 
   This code is temporary to pyramide down data like Spec Array
   It's written in C++ for speed but not optimized at all
*/
template <class IN,class OUT>
void down(const IN* src,
	  int width,int height,
	  int ox,int oy,
	  int cropwidth,int cropheight,
	  double xscale,double yscale,OUT *dest)
{
  double xscale_inv = 1./xscale;
  double yscale_inv = 1./yscale;
  const IN *_src = src + (width * oy);
  double yscale_loop = yscale_inv;
  int destwidth = int(ceil(cropwidth * xscale));
  for(int aLineId = 0;aLineId < cropheight;++aLineId)
    {
      double xscale_loop = xscale_inv;
      _src += ox;
      OUT *aDPixel = dest + int(aLineId * yscale) * destwidth;

      if(yscale_loop < 1e-6) yscale_loop = yscale_inv;
      
      for(int aPos = 0;aPos < cropwidth;++aPos,++_src)
	{
	  OUT pixel,comppixel;
	  if(yscale_loop < 1.) {pixel = OUT(*_src * yscale_loop);comppixel = OUT(*_src - pixel);}
	  else pixel = *_src,comppixel = 0.;


	  if(xscale_loop < 1e-6)
	    {
	      xscale_loop = xscale_inv;
	      ++aDPixel;
	      *aDPixel += pixel;
	      if(yscale_loop < 1.) // 2 line copy
		*(aDPixel + destwidth) += comppixel;
	    }
	  else if(xscale_loop < 1.)	// cross pixel
	    {
	      OUT pixelValue = OUT(pixel * xscale_loop);
	      *aDPixel += pixelValue;
	      *(aDPixel + 1) += pixel - pixelValue;
	      if(yscale_loop < 1.) // 2 line copy
	        {
		  pixelValue = OUT(comppixel * xscale_loop);
		  *(aDPixel + destwidth) += pixelValue;
		  *(aDPixel + destwidth + 1) += comppixel - pixelValue;
		}
	      xscale_loop = xscale_inv + xscale_loop;
	      ++aDPixel;
	    }
	  else
	    {
	      *aDPixel += pixel;
	      if(yscale_loop < 1.) // 2 lines copy
		*(aDPixel + destwidth) += comppixel;
	    }
	  xscale_loop -= 1.;
	}
      if(yscale_loop < 1.){yscale_loop = yscale_inv + yscale_loop;}
      yscale_loop -= 1.;
      _src += width - ox - cropwidth;
    }
}

template <class IN,class OUT>
void normalize(const IN *src,OUT * dest,int lineNb,int srcwidth,int destwidth,double coef)
{
  for(int lineID = 0;lineID < lineNb;++lineID)
    {
      const IN *_src = src + lineID * srcwidth;
      for(int cId = destwidth;cId;--cId,++_src,++dest)
	*dest = OUT(*_src * coef);
    }
}

