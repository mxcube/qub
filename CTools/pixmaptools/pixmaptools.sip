

%Import qt/qtmod.sip


%Module pixmaptools 0

%ModuleHeaderCode
extern "C" { void pixmap_import_array();}
%End

%PostInitialisationCode
pixmap_import_array();
%End
%Doc
<h1>Class IO</h1>
<p>
This class was copied from KPixmapIO and just rename IO
</p>
%End

class IO
{

%TypeHeaderCode
#include <pixmaptools_io.h>
%End

public:
    IO();
    ~IO();

    /**
     * Convert an image to a pixmap.
     * @param image The image to convert.
     * @return The pixmap containing the image.
     */
    QPixmap convertToPixmap(const QImage&);
    
    /**
     * Convert a pixmap to an image.
     * @param pixmap The pixmap to convert.
     * @return The image.
     */
    QImage convertToImage(const QPixmap&);

    /**
     * Bitblt an image onto a pixmap.
     * @param dst The destination pixmap.
     * @param dx Destination x offset.
     * @param dy Destination y offset.
     * @param src The image to load.
     */
    void putImage(QPixmap*,int,int,const QImage *);

    /**
     * This function is identical to the one above. It only differs in the
     * arguments it accepts.
     */
    void putImage(QPixmap*,const QPoint &,const QImage *);

    /**
     * Transfer (a part of) a pixmap to an image.
     * @param src The source pixmap.
     * @param sx Source x offset.
     * @param sy Source y offset.
     * @param sw Source width.
     * @param sh Source height.
     * @return The image.
     */
    QImage getImage(const QPixmap*,int,int,int,int);

    /**
     * This function is identical to the one above. It only differs in the
     * arguments it accepts.
     */
    QImage getImage(const QPixmap*,const QRect&);

    /**
     * Shared memory allocation policies.
     */
    enum ShmPolicies {
	ShmDontKeep,
	ShmKeepAndGrow
    };
    /**
     * Set the shared memory allocation policy. See the introduction for
     * IO for a discussion.
     * @param policy The alloction policy.
     */
    void setShmPolicy(int);

    /**
     * Pre-allocate shared memory. IO will be able to transfer images
     * up to this size without resizing.
     * @param size The size of the image in @em pixels.
     */
    void preAllocShm(int);
};

%Doc
<h1>Class LUT</h1>
<p>
This class is a lookup for colormap
</p>
%End

class LUT
{
%TypeHeaderCode
#include <pixmaptools_lut.h>
%End

public :
  enum mapping_meth {LINEAR,LOG};
  
public:
  class Palette
  {
%TypeHeaderCode
#include <pixmaptools_lut.h>
%End
  public:
    enum palette_type {GREYSCALE,TEMP,RED,GREEN,BLUE,REVERSEGREY,MANY,USER};
    enum mode {RGBX,BGRX};
    enum endian {LSB,MSB};

    explicit Palette(palette_type = USER,mode = RGBX);
%TypeCode
#define PY_ARRAY_UNIQUE_SYMBOL _PixmapNumpyArray
#include "numpy/arrayobject.h"
#include <iostream>
using namespace std;
extern "C"
{
  void pixmap_import_array()
  {
    import_array();
  }
}
template<class IN> void _create_palette_from_data(unsigned int *aDestPalette,const IN *aSrcPalette)
{
  Py_BEGIN_ALLOW_THREADS;
  for(int i = 0;i < 0x10000;++i,++aDestPalette,aSrcPalette += 4)
     {
      *aDestPalette  = aSrcPalette[0] & 0xff;
      *aDestPalette |= (aSrcPalette[1] & 0xff) << 8;
      *aDestPalette |= (aSrcPalette[2] & 0xff) << 16;
      *aDestPalette |= (aSrcPalette[3] & 0xff) << 24;	
     }
  Py_END_ALLOW_THREADS;
}
%End
    SIP_PYOBJECT getPaletteData();
%MethodCode
  unsigned int *aPaletteDataPt;
  int aSize;
  Py_BEGIN_ALLOW_THREADS;
  sipCpp->getPaletteData(aPaletteDataPt,aSize);
  Py_END_ALLOW_THREADS;
  sipRes = PyString_FromStringAndSize((const char *)aPaletteDataPt,aSize);
  delete aPaletteDataPt;
%End
    void setPaletteData(SIP_PYOBJECT);
%MethodCode
  PyArrayObject *colormapData;
  if(!(colormapData = (PyArrayObject*)PyArray_ContiguousFromObject(a0,NPY_NOTYPE,0,0)))
    {
      LutError *sipExceptionCopy = new LutError("Couldn't create an array");	
      sipRaiseClassException(sipClass_LutError,sipExceptionCopy);
      return NULL;
    }
   else
    {	
	int aNbVal = 1;
	for(int i = 0;i < colormapData->nd;++i)
	    aNbVal *= colormapData->dimensions[i];
	if(aNbVal != (0x10000 * 4))
	   {
	      LutError *sipExceptionCopy = new LutError("Palette must have 65536 entry of RBGX or BGRX");
      	      sipRaiseClassException(sipClass_LutError,sipExceptionCopy);
              Py_DECREF(colormapData);
	      return NULL;
	   }
	unsigned int aTmpPalette[0x10000];
	switch(colormapData->descr->type_num)
	{
 	 case NPY_BYTE:
	 case NPY_UBYTE:
	      _create_palette_from_data(aTmpPalette,(unsigned char*)colormapData->data);break;
         case NPY_SHORT:
	 case NPY_USHORT:
	      _create_palette_from_data(aTmpPalette,(unsigned short*)colormapData->data);break;
         case NPY_INT:
	 case NPY_UINT:
	       _create_palette_from_data(aTmpPalette,(unsigned int*)colormapData->data);break;
	 case NPY_LONG:
	 case NPY_ULONG:
               _create_palette_from_data(aTmpPalette,(unsigned long*)colormapData->data);break;
	 default:
	  {
	      LutError *sipExceptionCopy = new LutError("Palette type can by char,int,long,short");
      	      sipRaiseClassException(sipClass_LutError,sipExceptionCopy);
              Py_DECREF(colormapData);
	      return NULL;
          }
	}
	try
	{
	  sipCpp->setPaletteData(aTmpPalette,sizeof(aTmpPalette));
	}
	catch(LutError &err)
	{
	      LutError *sipExceptionCopy = new LutError(err);
      	      sipRaiseClassException(sipClass_LutError,sipExceptionCopy);
              Py_DECREF(colormapData);
	      return NULL;
	}
	
	Py_DECREF(colormapData);
    }
%End
    void fillPalette(palette_type) throw();
    void fillSegment(int from,int to,
		     double R1,double G1,double B1,
		     double R2,double G2,double B2) throw(LutError);
  };
%TypeCode
#define PY_ARRAY_UNIQUE_SYMBOL _PixmapNumpyArray
#define NO_IMPORT_ARRAY
#include "numpy/arrayobject.h"
#include "sippixmaptoolsLutError.h"
#include "sipqtQImage.h"

#define MAP_FUNCTION \
  PyArrayObject *src; \
  if(!(src = (PyArrayObject*)PyArray_ContiguousFromObject(a0,NPY_NOTYPE,2,2))) \
    { \
      LutError *sipExceptionCopy = new LutError("Input Array must be a 2x2 array"); \
      sipRaiseClassException(sipClass_LutError,sipExceptionCopy); \
      return NULL; \
    } \
    int column,row; \
    column = src->dimensions[1]; \
    row = src->dimensions[0]; \
    PyObject *aRImage;\
    switch(src->descr->type_num) \
    { \
	case NPY_BYTE: \
		{ \
		MAP_IMAGE(char); \
		sipRes = Py_BuildValue("(O(b,b))",aRImage,aMin,aMax); \
		break; \
		} \
	case NPY_UBYTE: \
		{ \
		MAP_IMAGE(unsigned char); \
		sipRes = Py_BuildValue("(O(B,B))",aRImage,aMin,aMax); \
		break; \
		} \
         case NPY_SHORT: \
		{ \
		MAP_IMAGE(short); \
		sipRes = Py_BuildValue("(O(h,h))",aRImage,aMin,aMax); \
		break; \
		} \
	 case NPY_USHORT: \
		{ \
		MAP_IMAGE(unsigned short); \
		sipRes = Py_BuildValue("(O(H,H))",aRImage,aMin,aMax); \
		break; \
		} \
         case NPY_INT: \
		{ \
		MAP_IMAGE(int); \
		sipRes = Py_BuildValue("(O(i,i))",aRImage,aMin,aMax); \
		break; \
		} \
	 case NPY_UINT: \
		{ \
		MAP_IMAGE(unsigned int); \
		sipRes = Py_BuildValue("(O(I,I))",aRImage,aMin,aMax); \
		break; \
		} \
	 case NPY_LONG: \
		{ \
		MAP_IMAGE(long); \
		sipRes = Py_BuildValue("(O(l,l))",aRImage,aMin,aMax); \
		break; \
		} \
	 case NPY_ULONG: \
		{ \
		MAP_IMAGE(unsigned long); \
		sipRes = Py_BuildValue("(O(k,k))",aRImage,aMin,aMax); \
		break; \
		} \
	 case NPY_FLOAT: \
		{ \
		MAP_IMAGE(float); \
		sipRes = Py_BuildValue("(O(f,f))",aRImage,aMin,aMax); \
		break; \
		} \
	 case NPY_DOUBLE: \
		{ \
		MAP_IMAGE(double); \
		sipRes = Py_BuildValue("(O(d,d))",aRImage,aMin,aMax); \
		break; \
		} \
	 default: \
	  { \
	      LutError *sipExceptionCopy = new LutError("Input Array type not supported"); \
      	      sipRaiseClassException(sipClass_LutError,sipExceptionCopy); \
              Py_DECREF(src); \
	      return NULL; \
          } \
     }\
 Py_DECREF(src);\
 Py_DECREF(aRImage);
%End

 static SIP_PYTUPLE map_on_min_max_val(SIP_PYOBJECT,Palette&,mapping_meth);
%MethodCode
#ifdef MAP_IMAGE
#undef MAP_IMAGE
#endif
#define MAP_IMAGE(TYPE)\
 TYPE aMin,aMax;\
 QImage aMappedImage;\
 Py_BEGIN_ALLOW_THREADS;\
 aMappedImage = LUT::map_on_min_max_val<TYPE>((TYPE*)src->data,column,row,*a1,a2,aMin,aMax);\
 Py_END_ALLOW_THREADS;\
 aRImage = sipConvertFromNewInstance(new QImage(aMappedImage),sipClass_QImage,NULL);
MAP_FUNCTION
%End

 static SIP_PYTUPLE map(SIP_PYOBJECT,Palette&,mapping_meth,double,double);
%MethodCode
#ifdef MAP_IMAGE
#undef MAP_IMAGE
#endif
#define MAP_IMAGE(TYPE)\
 TYPE aMin = (TYPE)a3;\
 TYPE aMax = (TYPE)a4;\
 QImage aMappedImage;\
 Py_BEGIN_ALLOW_THREADS;\
 aMappedImage = LUT::map<TYPE>((TYPE*)src->data,column,row,*a1,a2,aMin,aMax);\
 Py_END_ALLOW_THREADS;\
 aRImage = sipConvertFromNewInstance(new QImage(aMappedImage),sipClass_QImage,NULL);
MAP_FUNCTION
%End
};
class LutError
{
%TypeHeaderCode
#include <pixmaptools_lut.h>
%End

public:
  LutError(const char * aMessage);
  ~LutError();
 const char* msg() const;
};
