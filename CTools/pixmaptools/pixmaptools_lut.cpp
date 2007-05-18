#include "pixmaptools_lut.h"
#include <iostream>
#include <math.h>

#ifdef __SSE2__
// #include <mmintrin.h>
#include <pixmaptools_lut_sse.h>
#endif



struct LUT::XServer_Info {
  int byte_order;
  int pixel_size;
  unsigned int red_mask;
  unsigned int green_mask;
  unsigned int blue_mask;

  unsigned int rshift;
  unsigned int rbit;

  unsigned int gshift;
  unsigned int gbit;
  
  unsigned int bshift;
  unsigned int bbit;
};

struct lutConfiguration
{
  lutConfiguration()
  {
    LUT::XServer_Info &Xservinfo = _config[LUT::Palette::RGBX];
    Xservinfo.pixel_size = 4;
    short aVal = 1;
    Xservinfo.byte_order = *((char*)&aVal) ? LUT::Palette::LSB : LUT::Palette::MSB;
    Xservinfo.red_mask = 0x0000ff;
    Xservinfo.rshift = 0,Xservinfo.rbit = 8;

    Xservinfo.green_mask = 0x00ff00;
    Xservinfo.gshift = 8,Xservinfo.gbit = 8;

    Xservinfo.blue_mask = 0xff0000;
    Xservinfo.bshift = 16,Xservinfo.bbit = 8;

    Xservinfo = _config[LUT::Palette::BGRX];
    Xservinfo.pixel_size = 4;
    Xservinfo.byte_order = *((char*)&aVal) ? LUT::Palette::LSB : LUT::Palette::MSB;

    Xservinfo.red_mask = 0xff0000;
    Xservinfo.rshift = 16,Xservinfo.rbit = 8;

    Xservinfo.green_mask = 0x00ff00;
    Xservinfo.gshift = 8,Xservinfo.gbit = 8;

    Xservinfo.blue_mask = 0x0000ff00;
    Xservinfo.bshift = 0,Xservinfo.bbit = 8;
    double *aPt = _logCache;
    for(int i = 0;i < 0x10000;++i,++aPt)
      *aPt = log10(i);
  }
  const LUT::XServer_Info& getServerInfo(LUT::Palette::mode aMode){return _config[aMode];}
  inline double log(int aVal) const {return _logCache[aVal];}
  LUT::XServer_Info _config[2];
  double _logCache[0x10000];
};

static lutConfiguration theLutConfiguration;

typedef union {
  struct {
    unsigned char b1;
    unsigned char b2;
    unsigned char b3;
    unsigned char b4;
  } c;
  unsigned int p;
} swaptype;

/** @brief constructor of the Palette object
 *
 *  @param aMode there is two possible mode (RGBX or BGRX)
*/
LUT::Palette::Palette(palette_type pType,mode aMode) throw() : _mode(aMode)
{
  if(pType == USER) 
    memset(_dataPalette,0,sizeof(_dataPalette));
  else
    fillPalette(pType);
}
/** @brief create standard palette
 */
void LUT::Palette::fillPalette(palette_type aType) throw()
{
  const XServer_Info &config = theLutConfiguration.getServerInfo(_mode);
  switch(aType)
    {
    case TEMP:
      _fillSegment(config,0     , 0x4000,  0, 0, 1, 0, 1, 1);
      _fillSegment(config,0x4000, 0x8000,  0, 1, 1, 0, 1, 0);
      _fillSegment(config,0x8000, 0xc000,  0, 1, 0, 1, 1, 0);
      _fillSegment(config,0xc000, 0x10000, 1, 1, 0, 1, 0, 0);
      break;
    case MANY:
      _fillSegment(config,0     , 0x2aaa,  0, 0, 1, 0, 1, 1);
      _fillSegment(config,0x2aaa, 0x5555,  0, 1, 1, 0, 1, 0);
      _fillSegment(config,0x5555, 0x8000,  0, 1, 0, 1, 1, 0);
      _fillSegment(config,0x8000, 0xaaaa,  1, 1, 0, 1, 0, 0);
      _fillSegment(config,0xaaaa, 0xd555,  1, 0, 0, 1, 1, 0);
      _fillSegment(config,0xd555, 0x10000, 1, 1, 0, 1, 1, 1);
      break;
    case BLUE: 
      _fillSegment(config,0, 0x10000, 0, 0, 0, 0, 0, 1); break;
    case GREEN:
      _fillSegment(config,0, 0x10000, 0, 0, 0, 0, 1, 0); break;
    case RED:
      _fillSegment(config,0, 0x10000, 0, 0, 0, 1, 0, 0);break;
    case REVERSEGREY:
      _fillSegment(config,0, 0x10000, 1, 1, 1, 0, 0, 0);break;
    case GREYSCALE:
    default:
      _fillSegment(config,0, 0x10000, 0, 0, 0, 1, 1, 1);
      break;
    }
}
/**
 * @brief fill a contigus segment of the palette
 * @param from first index of the segment
 * @param to last index of the segment
 * @param RGB -> R = R1 + (R2 - R1) * (i-from) / (to - from)
 */
void LUT::Palette::fillSegment(int from,int to,
			       double R1,double G1,double B1,
			       double R2,double G2,double B2) throw(LutError)
{
  const XServer_Info &config = theLutConfiguration.getServerInfo(_mode);
  if(from < 0)
    throw LutError("fillSegment : from must be > 0");
  if(to > 0x10000) 
    throw LutError("fillSegment : to must be lower or equal to 65536");
  if(from > to)
    throw LutError("fillSegment : form must be lower than to");
  _fillSegment(config,from,to,R1,G1,B1,R2,G2,B2);
}
/// @brief set the data palette
void LUT::Palette::setPaletteData(const unsigned int *aPaletteDataPt,int aSize) throw(LutError)
{
  if(aSize != sizeof(int) * 0x10000)
    throw LutError("setPaletteData : Palette must be have 65536 value");
  memcpy(_dataPalette,aPaletteDataPt,aSize);
}

///@brief get the data palette
void LUT::Palette::getPaletteData(unsigned int * &aPaletteDataPt,int &aSize)
{
  aPaletteDataPt = new unsigned int[0x10000];
  memcpy(aPaletteDataPt,_dataPalette,sizeof(unsigned int) * 0x10000);
  aSize = sizeof(unsigned int) * 0x10000;
}
///@brief util to fill the palette
void LUT::Palette::_fillSegment(const XServer_Info &Xservinfo,
				int from, int to,
				double R1,double G1,double B1,double R2,double G2,double B2) throw()
{
  unsigned int *ptr;
  int R, G, B;
  double Rcol, Gcol, Bcol, Rcst, Gcst, Bcst;
  double coef, width, rwidth, gwidth, bwidth; 
  swaptype value;

  /* R = R1 + (R2 - R1) * (i-from) / (to - from)
     palette_col = (int)(R * (2**rbit-1) + 0.5) << rshift |
     (int)(G * (2**gbit-1) + 0.5) << gshift |
     (int)(B * (2**bbit-1) + 0.5) << bshift
  */

  Rcol = (1<<Xservinfo.rbit) - 1;
  Rcst = Rcol * R1 + 0.5;
  Gcol = (1<<Xservinfo.gbit) - 1;
  Gcst = Gcol * G1 + 0.5;
  Bcol = (1<<Xservinfo.bbit) - 1;
  Bcst = Bcol * B1 + 0.5;
  width = double(to - from);
  rwidth = Rcol * (R2 - R1) / width;
  gwidth = Gcol * (G2 - G1) / width;
  bwidth = Bcol * (B2 - B1) / width;
  int diff = to-from;

#if defined (i386)
  if (Xservinfo.byte_order == LSB) 
    {
      for (ptr = _dataPalette + from,coef = 0;coef < diff;++coef,++ptr) 
	{
	  R = int(Rcst + rwidth * coef);
	  G = int(Gcst + gwidth * coef);
	  B = int(Bcst + bwidth * coef);
	  *ptr = (R << Xservinfo.rshift) | (G << Xservinfo.gshift) | (B << Xservinfo.bshift);
	}
    }
  else
    {
      for (ptr = _dataPalette + from,coef = 0;coef < diff;++coef,++ptr) 
	{
	  R = int(Rcst + rwidth * coef);
	  G = int(Gcst + gwidth * coef);
	  B = int(Bcst + bwidth * coef);
	  value.p = (R << Xservinfo.rshift) | (G << Xservinfo.gshift) | (B << Xservinfo.bshift);
	  *ptr = value.c.b1 << 24 | value.c.b2 << 16 | value.c.b3 << 8;
	}
    }
#else
  if (Xservinfo.byte_order == MSB) 
    {
      
      for (ptr = _dataPalette + from,coef = 0;coef < diff;++coef,++ptr) 
	{
	  R = int(Rcst + rwidth * coef);
	  G = int(Gcst + gwidth * coef);
	  B = int(Bcst + bwidth * coef);
	  *ptr = (R << Xservinfo.rshift) | (G << Xservinfo.gshift) | (B << Xservinfo.bshift);
	}
    }
  else
    {
      for (ptr = _dataPalette + from,coef = 0;coef < diff;++coef,++ptr) 
	{
	  R = int(Rcst + rwidth * coef);
	  G = int(Gcst + gwidth * coef);
	  B = int(Bcst + bwidth * coef);
	  value.p = (R << Xservinfo.rshift) | (G << Xservinfo.gshift) | (B << Xservinfo.bshift);
	  *ptr = value.c.b4 << 16 | value.c.b3 << 8 | value.c.b2;
	}
    }
#endif
}
///@brief calc a palette for the data
void LUT::Palette::_calcPalette(unsigned int palette[],int fmin, int fmax, 
				mapping_meth meth) throw()
{
  double lmin, lmax;
  /*
    SPS_LINEAR:   mapdata = A * data + B
    SPS_LOG   :   mapdata = (A * log(data)) + B
  */
  if (!fmin && meth != LUT::LINEAR) 
    fmin = 1;
  double A,B;
  if(fmax - fmin)
    {
    if (meth == LUT::LINEAR) 
      lmin = fmin,lmax = fmax;
    else
      lmin = log10(fmin),lmax = log10(fmax);

    A = 0xffff / (lmax - lmin);
    B = - (0xffff * lmin) / (lmax - lmin);

    double round_min;
    if(meth == LUT::LINEAR)
      round_min = A * fmin + B;
    else
      round_min = (A * log10(fmin)) + B;

    if(round_min < 0.0 && round_min > -1E-5 )
      B += round_min;
  }
  else 
    A = 1.0,B = 0.0;


  unsigned int *pal = palette;
  unsigned int *palend = palette;
  pal += fmin ; palend += fmax;
  if (meth == LINEAR) 
    for(int j = 0;pal <= palend;++j,++pal)
      *pal = *(_dataPalette + int(A * j)); 
  else
    for(int j = fmin;pal <= palend;++j,++pal)
      *pal = *(_dataPalette + int(A * theLutConfiguration.log(j) + B)); 
}

// LUT TEMPLATE
/** @brief transform <b>data</b> to an image using the palette give in args
 * 
 *  autoscale data on min/max
 *  @param data the data source array
 *  @param anImagePt a data dest array it size must be >= sizeof(int) * nb pixel
 *  @param column the number of column of the source data
 *  @param row the number of row of the source data
 *  @param aPalette the palette colormap used to transform source data to an image
 *  @param aMeth the mapping methode
 *  @param dataMin return the min data value
 *  @param dataMax return the max data value
 */
template<class IN> void LUT::map_on_min_max_val(const IN *data,unsigned int *anImagePt,int column,int row,Palette &aPalette,
						  mapping_meth aMeth,
						  IN &dataMin,IN &dataMax)
{
  _find_min_max(data,column * row,dataMin,dataMax);
  map(data,anImagePt,column,row,aPalette,aMeth,dataMin,dataMax);
}

/** @brief transform <b>data</b> to an image using the palette an dataMin and dataMax given in args
 *  
 *  simple look up between dataMin and dataMax
 *  @see map_on_min_max_val
 */
template<class IN> void _find_min_max(const IN *aData,int aNbValue,IN &dataMin,IN &dataMax)
{
  dataMax = dataMin = *aData;++aData;
  for(int i = 1;i < aNbValue;++i,++aData)
    {
      if(*aData > dataMax) dataMax = *aData;
      else if(*aData < dataMin) dataMin = *aData;
    }
}
#ifdef __SSE2__
/// @brief opti min/max unsigned short
template<> void _find_min_max(unsigned short const *aData,int aNbValue,
			      unsigned short &dataMin,unsigned short &dataMax)
{
  __m128i aMinVector,aMaxVector;
  if(((long)aData) & 0xf) // if True not 16 alligned mmx min/max
    {
      aMinVector = _mm_set1_epi64(*(__m64*)aData),aMaxVector = _mm_set1_epi64(*(__m64*)aData);
      aData += 4,aNbValue -= 4;
    }
  else
    aMinVector = _mm_set1_epi16(*aData),aMaxVector = _mm_set1_epi16(*aData);

  __m128i *data = (__m128i*)aData;
  for(;aNbValue >= 8;++data,aNbValue -= 8)
    {
      aMinVector = _mm_min_epi16(aMinVector,*data);
      aMaxVector = _mm_max_epi16(aMaxVector,*data);
    }

  if(aNbValue >= 4)		// mmx ending
    {
      __m64 *aLocalMinf = (__m64*)&aMinVector;
      __m64 *aLocalMins = aLocalMinf + 1;
      __m64 *aLocalMaxf = (__m64*)&aMaxVector;
      __m64 *aLocalMaxs = aLocalMaxf + 1;
      __m64 aLocalMin = _mm_min_pi16(*aLocalMinf,*aLocalMins);
      __m64 aLocalMax = _mm_max_pi16(*aLocalMaxf,*aLocalMaxs);
      aLocalMin = _mm_min_pi16(aLocalMin,*(__m64*)data);
      aLocalMax = _mm_max_pi16(aLocalMax,*(__m64*)data);
      short *aValPt = (short*)&aLocalMin;
      unsigned short aVal = int(*aValPt) + 0x7fff;
      dataMin = aVal,dataMax = aVal;
      ++aValPt;
      for(int i = 3;i;--i,++aValPt)
	{
	  aVal = (int)*aValPt + 0x7fff;
	  if(aVal > dataMax) dataMax = aVal;
	  else if(aVal < dataMin) dataMin = aVal;
	}
      aValPt = (short*)&aLocalMax;
      for(int i = 4;i;--i,++aValPt)
	{
	  aVal = (int)*aValPt + 0x7fff;
	  if(aVal > dataMax) dataMax = aVal;
	  else if(aVal < dataMin) dataMin = aVal;
	}
    }
  else				// classic C++
    {
      short *aValPt = (short*)&aMinVector;
      unsigned aVal = int(*aValPt) + 0xffff;
      dataMin = aVal,dataMax = aVal;
      ++aValPt;
      for(int i = 7;i;--i,++aValPt)
	{
	  aVal = int(*aValPt) + 0xffff;
	  if(aVal > dataMax) dataMax = aVal;
	  else if(aVal < dataMin) dataMin = aVal;
	}
      aValPt = (short*)&aMaxVector;
      for(int i = 8;i;--i,++aValPt)
	{
	  aVal = int(*aValPt) + 0xffff;
	  if(aVal > dataMax) dataMax = aVal;
	  else if(aVal < dataMin) dataMin = aVal;
	}
      aData = (unsigned short * const)data;
      for(;aNbValue;--aNbValue,++aData)
	{
	  if(*aData > dataMax) dataMax = *aData;
	  else if(*aData < dataMin) dataMin = *aData;
	}
    }
  _mm_empty();
}
/// @brief opti for float
template<> void _find_min_max(const float *aData,int aNbValue,
			      float &dataMin,float &dataMax)
{
  min_max_float(aData,aNbValue,&dataMin,&dataMax);
}

#endif
template<class IN> void LUT::map(const IN *data,unsigned int *anImagePt,int column,int line,Palette &aPalette,
				 LUT::mapping_meth aMeth,
				 IN dataMin,IN dataMax)
{
  unsigned int aCachePalette[0x10000];
  unsigned int *aUsePalette;
  if(sizeof(IN) > sizeof(short))
    aUsePalette = aPalette._dataPalette;
  else
    {
      aUsePalette = aCachePalette;
      int aFmin = int(dataMin),aFmax = int(dataMax);
      if(aFmin < 0)
	{
	  aFmax += -aFmin;
	  aFmin = 0;
	}
      if(aFmax > 0xffff) aFmax = 0xffff;
      aPalette._calcPalette(aUsePalette,aFmin,aFmax,aMeth);
      aMeth = LINEAR;
    }
  _data_map(data,anImagePt,column,line,aMeth,aUsePalette,dataMin,dataMax);
}

template<class IN> void _data_map(const IN *data,unsigned int *anImagePt,int column,int line,
				  LUT::mapping_meth aMeth,unsigned int *aPalette,
				  IN dataMin,IN dataMax) throw()
{
  static const int mapmin = 0;
  static const int mapmax = 0xffff;

  double A, B;
  double lmin,lmax;
  IN shift = 0;
  if ((dataMax-dataMin) != 0) 
    {
      if (aMeth == LUT::LINEAR)
	{
	  lmin = double(dataMin);
	  lmax = double(dataMax);
	}
      else
	{
	  if(dataMin <= 0)
	    {
	      shift = -dataMin;
	      if(shift < 1e-6) shift += IN(1);
	      dataMax += shift;
	      dataMin += shift;
	    }
	  lmin = log10(dataMin);
	  lmax = log10(dataMax);
	}
      A = (mapmax - mapmin) / (lmax - lmin);
      B = mapmin - ((mapmax - mapmin) * lmin) / (lmax-lmin);
    }
  else 
    {
      A = 1.0;
      B = 0.0;
    }
  if(aMeth == LUT::LINEAR)
    _linear_data_map(data,anImagePt,column,line,aPalette,A,B,dataMin,dataMax);
  else
    {
      if(shift < 1e-6)
	_log_data_map(data,anImagePt,column,line,aPalette,A,B,dataMin,dataMax);
      else
	_log_data_map_shift(data,anImagePt,column,line,aPalette,A,B,dataMin,dataMax,shift);
    }
}

// LINEAR MAPPING FCT

template<class IN> void _linear_data_map(const IN *data,unsigned int *anImagePt,int column,int line,
					   unsigned int *palette,double A,double B,
					   IN dataMin,IN dataMax) throw()
{
  int aNbPixel = column * line;
  unsigned int *anImageEnd = anImagePt + aNbPixel;
    for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
       IN val=*data;
       if (val >= dataMax) 
 	*anImagePt = *(palette + 0xffff);
       else if  (val > dataMin)
	 *anImagePt = *(palette + long(A * val + B));
       else  
	 *anImagePt = *palette; 
    }
}

///@brief opti for unsigned short
template<> void _linear_data_map(unsigned short const *data,unsigned int *anImagePt,int column,int line,
				   unsigned int *palette,double,double,
				   unsigned short dataMin,unsigned short dataMax) throw()
{
  int aNbPixel = column * line;
  unsigned int *anImageEnd = anImagePt + aNbPixel;
  for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
      if(*data >= dataMax)
	*anImagePt = *(palette + dataMax);
      else if(*data > dataMin)
	*anImagePt = *(palette + *data);
      else
	*anImagePt = *palette;
    }
}

///@brief opti for short
template<> void _linear_data_map(const short *data,unsigned int *anImagePt,int column,int line,
				   unsigned int *palette,double,double,
				   short dataMin,short dataMax) throw()
{
  palette += long(ceil((dataMax - dataMin) / 2.));
  int aNbPixel = column * line;
  unsigned int *anImageEnd = anImagePt + aNbPixel;
  for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
      if(*data >= dataMax)
	*anImagePt = *(palette + dataMax);
      else if(*data > dataMin)
	*anImagePt = *(palette + *data);
      else
	*anImagePt = *palette;
    }
}

///@brief opti for char
template<> void _linear_data_map(const char *data,unsigned int *anImagePt,int column,int line,
				   unsigned int *palette,double,double,
				   char dataMin,char dataMax) throw()
{
  palette += long(ceil((dataMax - dataMin) / 2.));
  int aNbPixel = column * line;
  unsigned int *anImageEnd = anImagePt + aNbPixel;
  for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
      if(*data >= dataMax)
	*anImagePt = *(palette + dataMax);
      else if(*data > dataMin)
	*anImagePt = *(palette + *data);
      else
	*anImagePt = *palette;
    }
}
///@brief opti for unsigned char
template<> void _linear_data_map(unsigned char const *data,unsigned int *anImagePt,int column,int line,
				   unsigned int *palette,double,double,
				   unsigned char dataMin,unsigned char dataMax) throw()
{
  int aNbPixel = column * line;
  unsigned int *anImageEnd = anImagePt + aNbPixel;
  for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
      if(*data >= dataMax)
	*anImagePt = *(palette + dataMax);
      else if(*data > dataMin)
	*anImagePt = *(palette + *data);
      else
	*anImagePt = *palette;
    }
}
#ifdef __SSE2__
//@brief opti for float with sse2
template<> void _linear_data_map(const float *aData,unsigned int *anImagePt,int column,int line,
				   unsigned int *palette,double A,double B,
				   float dataMin,float dataMax) throw()
{
  int aNbPixel = column * line;
  if(((long)aData) & 0xf) // if True not 16 alligned standard lookup
    for(int i = 2;i;--i,--aNbPixel,++aData,++anImagePt)	// Std Lookup
      {
	float val=*aData;
	if (val >= dataMax) 
	  *anImagePt = *(palette + 0xffff);
	else if  (val > dataMin)
	  *anImagePt = *(palette + long(A * val + B));
	else  
	  *anImagePt = *palette; 
      }
  __m128 AFactor,BFactor;
  AFactor = _mm_set1_ps(A),BFactor = _mm_set1_ps(B);
  __m128i aMaxVal = _mm_set1_epi32(0xffff),aMinVal = _mm_set1_epi32(0x0000);
  __m128i aMaskPaletteMax = _mm_set1_epi32(0xffff0000);
  __m128 *data = (__m128*)aData;
  void *aBufferPt;
  posix_memalign(&aBufferPt,16,sizeof(int) << 3); // 2 __m128i buffer for sse flush avoid 
  struct IndexStruct
  {
    IndexStruct *next;
    unsigned int *data;
  };
  IndexStruct aTab[] = {IndexStruct(),IndexStruct()};
  aTab[0].next = &aTab[1],aTab[1].next = &aTab[0];
  aTab[0].data = (unsigned int*)aBufferPt,aTab[1].data = ((unsigned int*)aBufferPt) + 4;
  IndexStruct *aStructIndexPt = aTab;
  //FIRST 4 pixel
  __m128i *index = (__m128i*)aStructIndexPt->data;
  __m128 aResult = _mm_mul_ps(AFactor,*data);
  aResult = _mm_add_ps(BFactor,aResult);
  *index = _mm_cvtps_epi32(aResult);
  __m128i maskgt = _mm_cmpgt_epi32(*index,aMaxVal);
  __m128i masklt = _mm_cmplt_epi32(*index,aMinVal);
  maskgt = _mm_and_si128(maskgt,aMaskPaletteMax);
  *index = _mm_andnot_si128(maskgt,*index);
  *index = _mm_andnot_si128(masklt,*index);
  ++data,aNbPixel -=4,aStructIndexPt = aStructIndexPt->next;

  for(; aNbPixel >= 4;aNbPixel -= 4,++data,++index,aStructIndexPt = aStructIndexPt->next)
    {
      index = (__m128i*)aStructIndexPt->data;
      aResult = _mm_mul_ps(AFactor,*data);

      unsigned *aPaletteIndexPt = aStructIndexPt->next->data;
      *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt,++aPaletteIndexPt;
      *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt,++aPaletteIndexPt;

      aResult = _mm_add_ps(BFactor,aResult);
      *index = _mm_cvtps_epi32(aResult);
      maskgt = _mm_cmpgt_epi32(*index,aMaxVal);
      masklt = _mm_cmplt_epi32(*index,aMinVal);
      maskgt = _mm_and_si128(maskgt,aMaskPaletteMax);
      *index = _mm_andnot_si128(maskgt,*index);
      *index = _mm_andnot_si128(masklt,*index);

      *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt,++aPaletteIndexPt;
      *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt;

    }
  _mm_mfence();			// FLUSH
  //LAST 4 pixels
  unsigned *aPaletteIndexPt = aStructIndexPt->next->data;
  *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt,++aPaletteIndexPt;
  *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt,++aPaletteIndexPt;
  *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt,++aPaletteIndexPt;
  *anImagePt = *(palette + *aPaletteIndexPt);++anImagePt;

  free(aBufferPt);
  //END Std lookup
  aData = (float*)data;
  for(;aNbPixel;--aNbPixel,++aData,++anImagePt)
    {
      float val=*aData;
      if (val >= dataMax) 
 	*anImagePt = *(palette + 0xffff);
      else if  (val > dataMin)
	*anImagePt = *(palette + long(A * val + B));
      else  
	*anImagePt = *palette;
    }
}
#endif
// LOG MAPPING FCT

template<class IN> void _log_data_map(const IN *data,unsigned int *anImagePt,int column,int line,
				      unsigned int *aPalette,double A,double B,
				      IN dataMin,IN dataMax) throw()
{
  int aNbPixel = column * line;
  register unsigned int *anImageEnd = anImagePt + aNbPixel;
  register unsigned int *palette = aPalette;
  for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
      IN val=*data;
      if (val >= dataMax)
	*anImagePt = *(palette + 0xffff) ;
      else if  (val > dataMin)
	*anImagePt = *(palette + long(A * log10(val) + B));
      else
	*anImagePt = *palette ;
    }
}

template<class IN> void _log_data_map_shift(const IN *data,unsigned int *anImagePt,int column,int line,
					    unsigned int *aPalette,double A,double B,
					    IN dataMin,IN dataMax,IN shift) throw()
{
  int aNbPixel = column * line;
  register unsigned int *anImageEnd = anImagePt + aNbPixel;
  register unsigned int *palette = aPalette;
  for(;anImagePt != anImageEnd;++anImagePt,++data)
    {
      IN val=*data;
      val += shift;
      if (val >= dataMax)
	*anImagePt = *(palette + 0xffff) ;
      else if  (val > dataMin)
	*anImagePt = *(palette + long(A * log10(val + B)));
      else
	*anImagePt = *palette ;
    }
}

void init_template()
{
#define INIT_MAP(TYPE)							\
  {									\
    TYPE aMin,aMax;							\
    unsigned int *anImagePt = NULL;					\
    LUT::map_on_min_max_val((TYPE*)aBuffer,anImagePt,0,0,palette,LUT::LINEAR,aMin,aMax); \
    std::cout << aMin << aMax << *anImagePt << std::endl;		\
  }
  LUT::Palette palette = LUT::Palette();
  char *aBuffer = new char[16];
  INIT_MAP(char);
  INIT_MAP(unsigned char);
  INIT_MAP(short);
  INIT_MAP(unsigned short);
  INIT_MAP(int);
  INIT_MAP(unsigned int);
  INIT_MAP(long);
  INIT_MAP(unsigned long);
  INIT_MAP(float);
  INIT_MAP(double);
  delete [] aBuffer;
}
