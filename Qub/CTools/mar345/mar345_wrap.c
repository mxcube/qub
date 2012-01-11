#include <Python.h>
#include <stdlib.h>
#include <numpy/arrayobject.h>

#include "mar345_header.h"

#define PACKIDENTIFIER "\nCCP4 packed image, X: %04d, Y: %04d\n"

extern void unpack_word(FILE*,int,int,short*);

static PyObject* getData(PyObject *self, PyObject *args)
{
  PyObject *fileSrc;
  FILE *inputFile;
  PyObject *aReturnArray = NULL;

  if(PyArg_ParseTuple(args,"O",&fileSrc) &&
     PyFile_Check(fileSrc))
    {
      inputFile = PyFile_AsFile(fileSrc);
      if(inputFile)
	{
	  char header[BUFSIZ];
	  int x = 0,y = 0,i = 0,c = 0;
	  header[0] = '\n';
	  header[1] = 0;

	  fseek(inputFile,4096,SEEK_SET); /* skip header */
	  
	  while ((c != EOF) && ((x == 0) || (y == 0))) 
	    {
	      c = i = x = y = 0;
	    
	      while ((++i < BUFSIZ) && (c != EOF) && (c != '\n'))
		if ((header[i] = c = getc(inputFile)) == '\n')
		  if(sscanf(header, PACKIDENTIFIER, &x, &y) == 2)
		    {
		      int dimension[] = {x,y};
		      aReturnArray = PyArray_FromDims(2,dimension,NPY_USHORT);
		      unpack_word(inputFile, x, y,(short*)((PyArrayObject*)aReturnArray)->data);
		      break;
		    }
	    }
	}
    }
  return aReturnArray;
}

static PyObject* getInfo(PyObject *self, PyObject *args)
{
  PyObject *fileSrc;
  FILE *inputFile;
  PyObject *aReturnDict = NULL;

  if(PyArg_ParseTuple(args,"O",&fileSrc) &&
     PyFile_Check(fileSrc))
    {
      MAR345_HEADER MarHeader;
      PyObject *val = NULL;
      aReturnDict = PyDict_New();
      inputFile = PyFile_AsFile(fileSrc);

      MarHeader = Getmar345Header(inputFile);

      val = PyString_FromString(MarHeader.version);PyDict_SetItemString(aReturnDict,"version",val);Py_DECREF(val);
      val = PyString_FromString(MarHeader.program);PyDict_SetItemString(aReturnDict,"program",val);Py_DECREF(val);

      /* Scanner specific things */
      val = PyInt_FromLong((long)MarHeader.scanner);PyDict_SetItemString(aReturnDict,"scanner",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.size);PyDict_SetItemString(aReturnDict,"size",val);Py_DECREF(val);
      val = PyString_FromString(MarHeader.mode ? "TIME" : "DOSE" );PyDict_SetItemString(aReturnDict,"mode",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.high);PyDict_SetItemString(aReturnDict,"high",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.pixels);PyDict_SetItemString(aReturnDict,"pixels",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.adc_A);PyDict_SetItemString(aReturnDict,"adc_A",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.adc_B);PyDict_SetItemString(aReturnDict,"adc_B",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.add_A);PyDict_SetItemString(aReturnDict,"add_A",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.add_B);PyDict_SetItemString(aReturnDict,"add_B",val);Py_DECREF(val);

      val = PyInt_FromLong((long)MarHeader.gap[0]);PyDict_SetItemString(aReturnDict,"gap_0",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[1]);PyDict_SetItemString(aReturnDict,"gap_1",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[2]);PyDict_SetItemString(aReturnDict,"gap_2",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[3]);PyDict_SetItemString(aReturnDict,"gap_3",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[4]);PyDict_SetItemString(aReturnDict,"gap_4",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[5]);PyDict_SetItemString(aReturnDict,"gap_5",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[6]);PyDict_SetItemString(aReturnDict,"gap_6",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.gap[7]);PyDict_SetItemString(aReturnDict,"gap_7",val);Py_DECREF(val);

      val = PyFloat_FromDouble((double)MarHeader.pixel_length);PyDict_SetItemString(aReturnDict,"pixel_length",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.pixel_height);PyDict_SetItemString(aReturnDict,"pixel_height",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.multiplier);PyDict_SetItemString(aReturnDict,"multiplier",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.xcen);PyDict_SetItemString(aReturnDict,"xcen",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.ycen);PyDict_SetItemString(aReturnDict,"ycen",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.roff);PyDict_SetItemString(aReturnDict,"roff",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.toff);PyDict_SetItemString(aReturnDict,"toff",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.gain);PyDict_SetItemString(aReturnDict,"gain",val);Py_DECREF(val);

      /* Experimental conditions for this image */
      val = PyFloat_FromDouble((double)MarHeader.time);PyDict_SetItemString(aReturnDict,"time",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.dosebeg);PyDict_SetItemString(aReturnDict,"dosebeg",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.doseend);PyDict_SetItemString(aReturnDict,"doseend",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.dosemin);PyDict_SetItemString(aReturnDict,"dosemin",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.dosemax);PyDict_SetItemString(aReturnDict,"dosemax",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.doseavg);PyDict_SetItemString(aReturnDict,"doseavg",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.dosesig);PyDict_SetItemString(aReturnDict,"dosesig",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.wave);PyDict_SetItemString(aReturnDict,"wave",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.dist);PyDict_SetItemString(aReturnDict,"dist",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.resol);PyDict_SetItemString(aReturnDict,"resol",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.phibeg);PyDict_SetItemString(aReturnDict,"phibeg",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.phiend);PyDict_SetItemString(aReturnDict,"phiend",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.omebeg);PyDict_SetItemString(aReturnDict,"omebeg",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.omeend);PyDict_SetItemString(aReturnDict,"omeend",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.theta);PyDict_SetItemString(aReturnDict,"theta",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.chi);PyDict_SetItemString(aReturnDict,"chi",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.phiosc);PyDict_SetItemString(aReturnDict,"phiosc",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.omeosc);PyDict_SetItemString(aReturnDict,"omeosc",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.dosen);PyDict_SetItemString(aReturnDict,"dosen",val);Py_DECREF(val);

      /* Generator settings */
      val = PyString_FromString(MarHeader.source);PyDict_SetItemString(aReturnDict,"source",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.kV);PyDict_SetItemString(aReturnDict,"kV",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.mA);PyDict_SetItemString(aReturnDict,"mA",val);Py_DECREF(val);
	
      /* Monochromator */
      val = PyString_FromString(MarHeader.filter);PyDict_SetItemString(aReturnDict,"filter",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.polar);PyDict_SetItemString(aReturnDict,"polar",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.slitx);PyDict_SetItemString(aReturnDict,"slitx",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.slity);PyDict_SetItemString(aReturnDict,"slity",val);Py_DECREF(val);

      /* Image statistics  */
      val = PyInt_FromLong((long)MarHeader.valmin);PyDict_SetItemString(aReturnDict,"valmin",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.valmax);PyDict_SetItemString(aReturnDict,"valmax",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.valavg);PyDict_SetItemString(aReturnDict,"valavg",val);Py_DECREF(val);
      val = PyFloat_FromDouble((double)MarHeader.valsig);PyDict_SetItemString(aReturnDict,"valsig",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.histbeg);PyDict_SetItemString(aReturnDict,"histbeg",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.histend);PyDict_SetItemString(aReturnDict,"histend",val);Py_DECREF(val);
      val = PyInt_FromLong((long)MarHeader.histmax);PyDict_SetItemString(aReturnDict,"histmax",val);Py_DECREF(val);

      /* Remark             */
      val = PyString_FromString(MarHeader.remark);PyDict_SetItemString(aReturnDict,"remark",val);Py_DECREF(val);

      /* Time of production */
      val = PyString_FromString(MarHeader.date);PyDict_SetItemString(aReturnDict,"date",val);Py_DECREF(val);
    }
  return aReturnDict;
}
static PyMethodDef MAR345[] = {
  {"getData",getData, METH_VARARGS,
   "get Mar345 image data"},
  {"getInfo",getInfo, METH_VARARGS,
   "get Mar345 image info"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initmar345(void)
{
  Py_InitModule("mar345",MAR345);
  import_array();
}
