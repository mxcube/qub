#include <Python.h>
#include <stdlib.h>
#include <Numeric/arrayobject.h>
#include "down.h"

#define DOWN_SIZE(type) \
{\
 down((type*)data,width,height,ox,oy,crop_width,crop_height,xscale,yscale,aDest);\
 aReturnArray = (PyArrayObject*)PyArray_FromDims(2,dimension,src->descr->type_num); \
 normalize(aDest,(type*)aReturnArray->data,aReturnHeight,aDestWidth,aReturnWidth,\
	   xscale * yscale);\
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
  double *aDest = (double*)calloc(sizeof(double),aDestWidth * aDestHeight);
  PyArrayObject *aReturnArray = NULL;
  int aReturnWidth = int(crop_width * xscale);
  int aReturnHeight = int(crop_height * yscale);
  int dimension[] = {aReturnHeight,aReturnWidth};
  switch (src->descr->type_num) 
    {
    case PyArray_UINT:
      DOWN_SIZE(unsigned);break;
    case PyArray_USHORT:
      DOWN_SIZE(unsigned short);break;
    case PyArray_LONG: 
      DOWN_SIZE(long);break;
    case PyArray_INT: 
      DOWN_SIZE(int);break;
    case PyArray_SHORT: 
      DOWN_SIZE(short);break;
    case PyArray_UBYTE: 
      DOWN_SIZE(unsigned char);break;
    case PyArray_CHAR:
    case PyArray_SBYTE: 
      DOWN_SIZE(char);break;
    case PyArray_FLOAT: 
      DOWN_SIZE(float);break;
    case PyArray_DOUBLE: 
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

extern "C"{static PyObject * _interpol(PyObject *self, PyObject *args);}

static PyObject *
_interpol(PyObject *self, PyObject *args)
{    
    /* required input parameters */              
    PyObject *xinput;        /* The tuple containing the xdata arrays */
    PyObject *yinput;        /* The array containing the ydata values */
    PyObject *xinter0;       /* The array containing the x values */

    /* local variables */
    PyArrayObject    *ydata, *result, **xdata, *xinter;
    long    i, j, k, l, jl, ju, offset, badpoint; 
    double  value, *nvalue, *x1, *x2, *factors;
    double  dhelp, yresult;
    double  dummy = -1.0;
    long    nd_y, nd_x, index1, npoints, *points, *indices;
    /*int         dimensions[1];*/
    int     dimensions[1];
    int     dim_xinter[1];
    double *helppointer;
    
    /* statements */        
    if (!PyArg_ParseTuple(args, "OOO|d", &xinput, &yinput,&xinter0,&dummy)){
      PyErr_SetString(DataFuncsError, "Parsing error");
      return NULL;
    }
    ydata = (PyArrayObject *)
             PyArray_CopyFromObject(yinput, PyArray_DOUBLE,0,0);
    if (ydata == NULL){
        PyErr_SetString(DataFuncsError,"Copy from Object error!\n");    
        return NULL;
    }
    nd_y = ydata->nd;
    if (nd_y == 0) {
        PyErr_SetString(DataFuncsError,"I need at least a vector!\n");
        Py_DECREF(ydata);
        return NULL;
    }
/*
    for (i=0;i<nd_y;i++){
        printf("Dimension %d = %d\n",i,ydata->dimensions[i]);    
    }
*/
    /* xdata parsing */
/*    (PyArrayObject *) xdata = (PyArrayObject *) malloc(nd_y * sizeof(PyArrayObject));*/
    xdata = (PyArrayObject **) malloc(nd_y * sizeof(PyArrayObject *));

    if (xdata == NULL){
        PyErr_SetString(DataFuncsError,"Error in memory allocation\n");
        return NULL;
    }
    if (PySequence_Size(xinput) != nd_y){
        PyErr_SetString(DataFuncsError,"xdata sequence of wrong length\n");
        return NULL;    
    }
    for (i=0;i<nd_y;i++){
       /* printf("i = %d\n",i);*/
        /*xdata[i] = (PyArrayObject *)
                    PyArray_CopyFromObject(yinput,PyArray_DOUBLE,0,0);
        */
        xdata[i] = (PyArrayObject *)
                    PyArray_CopyFromObject((PyObject *)
                    (PySequence_Fast_GET_ITEM(xinput,i)), PyArray_DOUBLE,0,0);
        if (xdata[i] == NULL){
            PyErr_SetString(DataFuncsError,"x Copy from Object error!\n");
            for (j=0;j<i;j++){
                Py_DECREF(xdata[j]);
            }
            free(xdata);
            Py_DECREF(ydata);  
            return NULL;
        }
    }
    
    /* check x dimensions are appropriate */
    j=0;
    for (i=0;i<nd_y;i++){
        nd_x = xdata[i]->nd;
        if (nd_x != 1) {
            PyErr_SetString(DataFuncsError,"I need a vector!\n");
            j++;
            break;
        }
        if (xdata[i]->dimensions[0] != ydata->dimensions[i]){
	  char buffer[128];
	  sprintf(buffer,"xdata[%ld] does not have appropriate dimension\n",i);
	  PyErr_SetString(DataFuncsError,buffer);
	  j++;
	  break;
        }
    }
    if (j) {
        for (i=0;i<nd_y;i++){
            Py_DECREF(xdata[i]);
        }
        free(xdata);
        Py_DECREF(ydata);
        return NULL;
    }    

    xinter = (PyArrayObject *) PyArray_ContiguousFromObject(xinter0, PyArray_DOUBLE,0,0);
    
    if (xinter->nd == 1){
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
    }else{
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
    helppointer = (double *) xinter->data;
/*    printf("npoints = %d\n",npoints);
    printf("ndimensions y  = %d\n",nd_y);
*/
    /* Parse the points to interpolate */    
    /* find the points to interpolate */
    points  = (long*)malloc((1 << nd_y) * nd_y * sizeof(int));
    indices = (long*)malloc(nd_y * sizeof(int));
    for (i=0;i<nd_y;i++){
        indices[i] = -1;
    }
    factors = (double*)malloc(nd_y * sizeof(double));
    dimensions [0] = npoints;
    
    result = (PyArrayObject *) 
             PyArray_FromDims(1,dimensions,PyArray_DOUBLE);

    for (i=0;i<npoints;i++){
        badpoint = 0;
        for (j=0; j< nd_y; j++){
            index1 = -1;
            if (badpoint == 0){
                value = *helppointer++;
                k=xdata[j]->dimensions[0] - 1;
                nvalue = (double *) (xdata[j]->data + k * xdata[j]->strides[0]);
                /* test against other version 
                valueold = PyFloat_AsDouble(
                    PySequence_Fast_GET_ITEM(PySequence_Fast_GET_ITEM(xinter0,i),j));
                if ( fabs(valueold-value) > 0.00001){
                    printf("i = %d, j= %d, oldvalue = %.5f, newvalue = %.5f\n",i,j,valueold, value);
                }
                */
                if (value >= *nvalue){
                    badpoint = 1;
                }else{
                    nvalue = (double *) (xdata[j]->data);
                    if (value < *nvalue){
                         badpoint = 1;
                    }
                }
                if (badpoint == 0){
                    if (1){
                        k = xdata[j]->dimensions[0];
                        jl = -1;
                        ju = k-1;
                        if (badpoint == 0){
                            while((ju-jl) > 1){
                                k = (ju+jl)/2;
                                nvalue = (double *) (xdata[j]->data + k * xdata[j]->strides[0]);
                                if (value >= *nvalue){
                                    jl=k;
                                }else{
                                    ju=k;                    
                                }            
                            }
                            index1=jl;
                        }
                    }
                    /* test against the other version */
                    if (0){
                        k=0;
                        ju = -1;
                        while(k < (xdata[j]->dimensions[0] - 1)){
                            nvalue = (double *) (xdata[j]->data + k * xdata[j]->strides[0]);
                            /*printf("nvalue = %g\n",*nvalue);*/
                            if (value >= *nvalue){
                                ju = k;
                             }
                            k++;
                        }
                        if (ju != index1){
			  char buffer[256];
			  sprintf(buffer,"i = %ld, j= %ld, value = %.5f indexvalue = %ld, newvalue = %ld\n",i,j,value,ju, index1);
			  PyErr_SetString(DataFuncsError,buffer);
                        }
                    }
                    if (index1 < 0){
                        badpoint = 1;
                    }else{
                        x1 = (double *) (xdata[j]->data + index1 * xdata[j]->strides[0]);
                        x2 = (double *) (xdata[j]->data + (index1+1) * xdata[j]->strides[0]);
                        factors[j] = (value - *x1) / (*x2 - *x1);
                        indices[j] = index1;
                    }
                }
            }else{
                helppointer++;
            }
        }
        if (badpoint == 1){
            yresult = dummy;
        }else{
          for (k=0;k<(pow(2,nd_y) * nd_y);k++){
                j = k % nd_y;
                if (nd_y > 1){
                    l = k /(2 * (nd_y - j) );
                }else{
                    l = k;
                }
                if ( (l % 2 ) == 0){ 
                    points[k] = indices[j];
                }else{
                    points[k] = indices[j] + 1;
                }
             /*   printf("l = %d ,points[%d] = %d\n",l,k,points[k]);*/
          } 
        /* the points to interpolate */
          yresult = 0.0;
          for (k=0;k<pow(2,nd_y);k++){
            dhelp =1.0;
            offset = 0;
            for (j=0;j<nd_y;j++){
                if (nd_y > 1){
                    l = ((nd_y * k) + j) /(2 * (nd_y - j) );
                }else{
                    l = ((nd_y * k) + j);
                }
                offset += points[(nd_y * k) + j] * (ydata -> strides[j]);
                /*printf("factors[%d] = %g\n",j,factors[j]);*/
                if ((l % 2) == 0){ 
                    dhelp = (1.0 - factors[j]) * dhelp;
                }else{
                    dhelp =  factors[j] * dhelp;
                }
            }
            yresult += *((double *) (ydata -> data + offset)) * dhelp;
          }
        }
       *((double *) (result->data +i*result->strides[0])) =  yresult;
    }
    free(points);
    free(indices);
    free(factors);
    for (i=0;i<nd_y;i++){
        Py_DECREF(xdata[i]);
    }
    free(xdata);
    Py_DECREF(ydata);
    Py_DECREF(xinter);

    return PyArray_Return(result);
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
