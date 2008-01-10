#ifndef _QWTTOOLS_SCALE_H
#define QWTTOOLS_SCALE_H
#include <qwt_scale_engine.h>

class QubTrunkNegLog10ScaleEngine : public QwtLog10ScaleEngine
{
 public:
  QubTrunkNegLog10ScaleEngine();
  virtual void 	autoScale (int maxNumSteps, double &x1, double &x2, double &stepSize) const;
  virtual QwtScaleTransformation *transformation() const;

  double minValue() const {return _minValue;}
  void setMinValue(double minValue) {_minValue = minValue;}
 private:
  double _minValue;
};
#endif
