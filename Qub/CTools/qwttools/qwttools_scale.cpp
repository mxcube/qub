#include <qwt_scale_map.h>

#include "qwttools_scale.h"

#include <iostream>

class _Transformation : public QwtScaleTransformation
{
public:
  _Transformation() : QwtScaleTransformation(QwtScaleTransformation::Other) {}
  virtual 	~_Transformation() {}
  virtual double xForm (double s, double s1, double s2, double p1, double p2) const
  {
    if(s <= 1e-12)
      return p1;
    else
      return p1 + (p2 - p1) / log(s2 / s1) * log(s / s1);
  }
  virtual double invXForm (double p, double p1, double p2, double s1, double s2) const
  {
    return (exp((p - p1) / (p2 - p1) * log(s2 / s1)) * s1);
  }

 virtual QwtScaleTransformation *copy() const
  {
    return new _Transformation();
  }
};

QubTrunkNegLog10ScaleEngine::QubTrunkNegLog10ScaleEngine() : QwtLog10ScaleEngine(),_minValue(1e-6)
{
}

void QubTrunkNegLog10ScaleEngine::autoScale(int maxNumSteps,
					 double &x1, double &x2,
					 double &stepSize) const
{
  if(x1 > x2) 
    {
      double tmp = x2;
      x2 = x1;
      x1 = tmp;
    }
  
  if(x1 <= 0) x1 = _minValue;
  QwtLog10ScaleEngine::autoScale(maxNumSteps,x1,x2,stepSize);
}

QwtScaleTransformation* QubTrunkNegLog10ScaleEngine::transformation() const
 {
   return new _Transformation();
 }
