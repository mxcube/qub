#include <Python.h>
#include <stdlib.h>
#include <numpy/arrayobject.h>
#include "down.h"

#define DOWN_SIZE(type) \
{\
  aReturnArray = (PyArrayObject*)PyArray_FromDims(2,dimension,src->descr->type_num); \
  Py_BEGIN_ALLOW_THREADS;						\
  down((type*)data,width,height,ox,oy,crop_width,crop_height,xscale,yscale,aDest); \
  normalize(aDest,(type*)aReturnArray->data,aReturnHeight,aDestWidth,aReturnWidth, \
	   xscale * yscale);\
  Py_END_ALLOW_THREADS;	    \
}

static PyObject *DataFuncsError;

extern "C"{static PyObject * down_size(PyObject *self, PyObject *args);}

static PyObject* down_size(PyObject *self, PyObject *args)
{
  PyArrayObject *src;
  PyObject *in_src;
  int ox,oy,crop_width,crop_height;
  double xscale,yscale;
  
  if(!PyArg_ParseTuple(args,"Oiiiidd",&in_src,
		       &ox,&oy,&crop_width,&crop_height,
		       &xscale,&yscale))
    return NULL;
  
  if(!(src = (PyArrayObject*)PyArray_ContiguousFromObject(in_src,PyArray_NOTYPE, 2, 2)))
    {
      PyErr_SetString(DataFuncsError, "Input Array could is not a 2x2 array");
      return NULL;
    }
  void *data = src->data;
  int width = src->dimensions[1];
  int height = src->dimensions[0];
  if(width < ox + crop_width) crop_width = width - ox;
  if(height < oy + crop_height) crop_height = height - oy;

  int aDestWidth = int(ceil(crop_width * xscale));
  int aDestHeight = int(ceil(crop_height * yscale));
  double *aDest = (double*)calloc(sizeof(double),aDestWidth * (aDestHeight + 1));
  PyArrayObject *aReturnArray = NULL;
  int aReturnWidth = int(crop_width * xscale);
  int aReturnHeight = int(crop_height * yscale);
  int dimension[] = {aReturnHeight,aReturnWidth};
  switch (src->descr->type_num) 
    {
    case NPY_UINT:
      DOWN_SIZE(unsigned);break;
    case NPY_USHORT:
      DOWN_SIZE(unsigned short);break;
    case NPY_LONG: 
      DOWN_SIZE(long);break;
    case NPY_INT: 
      DOWN_SIZE(int);break;
    case NPY_SHORT: 
      DOWN_SIZE(short);break;
    case NPY_UBYTE: 
      DOWN_SIZE(unsigned char);break;
    case NPY_CHAR:
    case NPY_BYTE: 
      DOWN_SIZE(char);break;
    case NPY_FLOAT: 
      DOWN_SIZE(float);break;
    case NPY_DOUBLE: 
      DOWN_SIZE(double);break;
    default:
      {
	char aBuffer[512];
	sprintf(aBuffer,"Input Array type not supported (%d)",src->descr->type_num);
	PyErr_SetString(DataFuncsError,aBuffer);
      }
      break;
    }
  free(aDest);
  Py_DECREF(src);
  return (PyObject*)aReturnArray;
}

template <class POINT_TYPE,class IN>
inline PyObject* _template_interpol(POINT_TYPE* helppointer,long nd_y,long npoints,double dummy,
				    PyArrayObject **xdata,PyArrayObject *ydata,
				    IN* ydataPointer)
{

  long *points  = (long*)malloc((1 << nd_y) * nd_y * sizeof(int));
  long *indices = (long*)malloc(nd_y * sizeof(int));
  for(int i=0;i<nd_y;i++) indices[i] = -1;

  double *factors = (double*)malloc(nd_y * sizeof(double));
  int dimensions [] = {npoints};
    
  PyArrayObject *result = (PyArrayObject *) 
    PyArray_FromDims(1,dimensions,PyArray_DOUBLE);
  long badpoint;
  long index1;
  for(int i=0;i<npoints;++i)
    {
      badpoint = 0;
      for(int j=0; j< nd_y; ++j,++helppointer)
	{
	  index1 = -1;
	  if (!badpoint)
	    {
	      double value = (double)*helppointer;
	      int k = xdata[j]->dimensions[0] - 1;
	      double *nvalue = (double *) (xdata[j]->data + k * xdata[j]->strides[0]);
	      if (value >= *nvalue)
		{
		  badpoint = 1;
		}
	      else
		{
		  nvalue = (double *) (xdata[j]->data);
		  if (value < *nvalue)
		    badpoint = 1;
		}

	      if(!badpoint)
		{
		  int k = xdata[j]->dimensions[0];
		  int jl = -1;
		  int ju = k-1;
		  if(!badpoint)
		    {
		      while((ju-jl) > 1)
			{
			  k = (ju+jl)/2;
			  nvalue = (double *) (xdata[j]->data + k * xdata[j]->strides[0]);
			  if (value >= *nvalue) jl=k;
			  else ju=k;                    
			}
		      index1=jl;
		    }
		  if (index1 < 0)
		    badpoint = 1;
		  else
		    {
		      double *x1 = (double *) (xdata[j]->data + index1 * xdata[j]->strides[0]);
		      double *x2 = (double *) (xdata[j]->data + (index1+1) * xdata[j]->strides[0]);
		      factors[j] = (value - *x1) / (*x2 - *x1);
		      indices[j] = index1;
		    }
		}
	    }
	}
      double yresult;
      if (badpoint == 1)
	yresult = dummy;
      else
	{
	  for(int k=0;k<((1 << nd_y) * nd_y);++k)
	    {
	      int j = k % nd_y;
	      long l = nd_y > 1 ? k /(2 * (nd_y - j)) : k;
	      points[k] = (l % 2) ? indices[j] + 1 : indices[j];
	    } 
	  /* the points to interpolate */
	  yresult = 0.0;
	  for(int k = 0;k < (1 << nd_y);++k)
	    {
	      double dhelp =1.0;
	      long offset = 0;
	      for(int j=0;j<nd_y;++j)
		{
		  long l = nd_y > 1 ? ((nd_y * k) + j) /(2 * (nd_y - j) ) : ((nd_y * k) + j);
		  offset += points[(nd_y * k) + j] * (ydata -> strides[j]);
		  dhelp = (l % 2) ? factors[j] * dhelp : (1.0 - factors[j]) * dhelp;
		}
	      IN dataValue = *((IN *) (ydata -> data + offset));
	      yresult += dataValue * dhelp;
	    }
	}
      *((double *) (result->data +i*result->strides[0])) =  yresult;
    }
  free(points);
  free(indices);
  free(factors);
  for(int i=0;i<nd_y;++i)
    Py_DECREF(xdata[i]);

  free(xdata);
  Py_DECREF(ydata);

  return PyArray_Return(result);
}

extern "C"{static PyObject * _interpol(PyObject *self, PyObject *args);}
#define INTERPOL(type1) \
switch(ydata->descr->type_num) \
  { \
  case NPY_BYTE:  \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(char*)ydata->data);break; \
  case NPY_UBYTE: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(unsigned char*)ydata->data);break; \
  case NPY_SHORT: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(short*)ydata->data);break; \
  case NPY_USHORT: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(unsigned short*)ydata->data);break; \
  case NPY_INT: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(int*)ydata->data);break; \
  case NPY_UINT: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(unsigned int*)ydata->data);break; \
  case NPY_LONG: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(long*)ydata->data);break; \
  case NPY_ULONG: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(unsigned long*)ydata->data);break; \
  case NPY_FLOAT: \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(float*)ydata->data);break; \
  case NPY_DOUBLE:  \
    result = _template_interpol((type1)xinter->data,nd_y,npoints,dummy,xdata,ydata,(double*)ydata->data);break; \
  default: \
    result = NULL; \
    break; \
  } 

static PyObject *
_interpol(PyObject *self, PyObject *args)
{    
  /* required input parameters */              
  PyObject *xinput;        /* The tuple containing the xdata arrays */
  PyObject *yinput;        /* The array containing the ydata values */
  PyObject *xinter0;       /* The array containing the x values */

  /* local variables */
  PyArrayObject    *ydata,**xdata, *xinter;
  double  dummy = -1.0;
  long    nd_y, nd_x, npoints;
  /*int         dimensions[1];*/
  int     dim_xinter[1];
  /* statements */        
  if(!PyArg_ParseTuple(args, "OOO|d", &xinput, &yinput,&xinter0,&dummy))
    {
      PyErr_SetString(DataFuncsError, "Parsing error");
      return NULL;
    }
  ydata = (PyArrayObject *)
    PyArray_ContiguousFromObject(yinput, NPY_NOTYPE,0,0);
  if(!ydata)
    {
      PyErr_SetString(DataFuncsError,"Copy from Object error!\n");    
      return NULL;
    }
  nd_y = ydata->nd;
  if(!nd_y)
    {
      PyErr_SetString(DataFuncsError,"I need at least a vector!\n");
      Py_DECREF(ydata);
      return NULL;
    }
  xdata = (PyArrayObject **) malloc(nd_y * sizeof(PyArrayObject *));
  
  if(!xdata)
    { 
      PyErr_SetString(DataFuncsError,"Error in memory allocation\n");
      return NULL;
    }
  if(PySequence_Size(xinput) != nd_y)
    {
      PyErr_SetString(DataFuncsError,"xdata sequence of wrong length\n");
      return NULL;    
    }
  for(int i=0;i<nd_y;++i)
    {
      xdata[i] = (PyArrayObject *)
	PyArray_CopyFromObject((PyObject *)
			       (PySequence_Fast_GET_ITEM(xinput,i)), PyArray_DOUBLE,0,0);
      if (xdata[i] == NULL){
	PyErr_SetString(DataFuncsError,"x Copy from Object error!\n");
	for(int j=0;j<i;j++)
	  Py_DECREF(xdata[j]);
	free(xdata);
	Py_DECREF(ydata);  
	return NULL;
      }
    }
    
  /* check x dimensions are appropriate */
  int j=0;
  for(int i=0;i<nd_y;++i){
    nd_x = xdata[i]->nd;
    if (nd_x != 1) {
      PyErr_SetString(DataFuncsError,"I need a vector!\n");
      j++;
      break;
    }
    if (xdata[i]->dimensions[0] != ydata->dimensions[i]){
      char buffer[128];
      sprintf(buffer,"xdata[%d] does not have appropriate dimension\n",i);
      PyErr_SetString(DataFuncsError,buffer);
      ++j;
      break;
    }
  }
  if(j)
    {
      for(int i=0;i<nd_y;++i)
	Py_DECREF(xdata[i]);
      free(xdata);
      Py_DECREF(ydata);
      return NULL;
    }    

  xinter = (PyArrayObject *) PyArray_ContiguousFromObject(xinter0, NPY_NOTYPE,0,0);
    
  if (xinter->nd == 1)
    {
      dim_xinter[0] = xinter->dimensions[0];
      dim_xinter[1] = 0;
      if (dim_xinter[0] != nd_y){
	PyErr_SetString(DataFuncsError,"Wrong size\n");
	for (j=0;j<nd_y;j++){
	  Py_DECREF(xdata[j]);
	}
	free(xdata);
	Py_DECREF(xinter);
	Py_DECREF(ydata);
	return NULL;
      }
    }
  else
    {
      dim_xinter[0] = xinter->dimensions[0];
      dim_xinter[1] = xinter->dimensions[1];
      if (dim_xinter[1] != nd_y){
	PyErr_SetString(DataFuncsError,"Wrong size\n");
	for (j=0;j<nd_y;j++){
	  Py_DECREF(xdata[j]);
	}
	free(xdata);
	Py_DECREF(xinter);
	Py_DECREF(ydata);
	return NULL;
      }
    }

  npoints = xinter->dimensions[0];
  PyObject *result = NULL;
  switch(xinter->descr->type_num)
    {
    case NPY_BYTE: 
      INTERPOL(char*);break;
    case NPY_UBYTE:
      INTERPOL(unsigned char*);break;
    case NPY_SHORT:
      INTERPOL(short*);break;
    case NPY_USHORT:
      INTERPOL(unsigned short*);break;
    case NPY_INT:
      INTERPOL(int*);break;
    case NPY_UINT:
      INTERPOL(unsigned int*);break;
    case NPY_LONG:
      INTERPOL(long*);break;
    case NPY_ULONG:
      INTERPOL(unsigned long*);break;
    case NPY_FLOAT:
      INTERPOL(float*);break;
    case NPY_DOUBLE: 
      INTERPOL(double*);break;
      break;
    default:
      result = NULL;
      break;
    }
  Py_DECREF(xinter);
  return result;
}




static PyMethodDef RESIZE[] = {
  {"down_size",down_size, METH_VARARGS,
   "Down size data"},
  {"interpol",_interpol, METH_VARARGS,
   "Down size data"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdatafuncs(void)
{
  PyObject *m = Py_InitModule("datafuncs",RESIZE);
  PyObject *d = PyModule_GetDict(m);

  DataFuncsError = PyErr_NewException("datafuncs.error", NULL, NULL);
  PyDict_SetItemString(d, "error", DataFuncsError);

  import_array();
}
