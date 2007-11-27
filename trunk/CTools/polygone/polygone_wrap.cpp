#include <Python.h>

#include "polygone.h"


extern "C"{static PyObject * points_inclusion(PyObject *self, PyObject *args);}
static PyObject *
points_inclusion(PyObject *self, PyObject *args)
{
  PyObject * pointList; /* the list of tuple (x,y) */
  PyObject * polygone;		// polygone vector list
  int aWindingFlag;
  if (!PyArg_ParseTuple( args, "O!O!|i",&PyList_Type,&pointList,
			 &PyList_Type,&polygone,&aWindingFlag))
    return NULL;

  int points_number = PyList_Size(pointList);
  std::vector<Polygone::Point> aPoint(points_number);
  for(int i = 0;i < points_number;++i)
    {
      PyObject* tuple = PyList_GetItem(pointList,i);
      PyObject* First = PySequence_GetItem(tuple,0);
      PyObject* Second = PySequence_GetItem(tuple,1);
      if(!First || !Second) 
	return NULL;
      aPoint[i].x = PyFloat_AsDouble(First);
      aPoint[i].y = PyFloat_AsDouble(Second);
    }
  
  int nb_polygone_point = PyList_Size(polygone);
  std::vector<Polygone::Point> aPolygone(nb_polygone_point + 1); // LAST == FIRST
  for(int i = 0;i < nb_polygone_point;++i)
    {
      PyObject *tuple = PyList_GetItem(polygone,i);
      PyObject* First = PySequence_GetItem(tuple,0);
      PyObject* Second = PySequence_GetItem(tuple,1);
      if(!First || !Second) 
	return NULL;
      aPolygone[i].x = PyFloat_AsDouble(First);
      aPolygone[i].y = PyFloat_AsDouble(Second);
    }
  aPolygone[nb_polygone_point].x = aPolygone[0].x;
  aPolygone[nb_polygone_point].y = aPolygone[0].y;
 


  std::list<int> aResultList;
  Py_BEGIN_ALLOW_THREADS;
  Polygone::points_inclusion(aPoint,aPolygone,aResultList,aWindingFlag);
  Py_END_ALLOW_THREADS;

  PyObject *aPythonReturnList = PyList_New(points_number);
  int i;
  std::list<int>::iterator l;
  for(i = 0,l = aResultList.begin();
      i < points_number;++i,++l)
    PyList_SetItem(aPythonReturnList,i,PyInt_FromLong(*l));
  return aPythonReturnList;
}

static PyMethodDef PolygonMethods[] = {
  {"points_inclusion", points_inclusion, METH_VARARGS,
   "Check if the point list is in the polygone and return a boolean list."},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpolygone(void)
{
  Py_InitModule("polygone",PolygonMethods);
}
