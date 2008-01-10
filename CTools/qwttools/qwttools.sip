%Import Qwt5/QwtModule.sip


%Module qwttools 0

%Doc
<h1>Class QubShiftLog10ScaleEngine</h1>
<p>
This class is a log scale and trunk negatives value
</p>
%End

class QubTrunkNegLog10ScaleEngine :  QwtLog10ScaleEngine
{
%TypeHeaderCode
#include <qwttools_scale.h>
%End
 public:
  QubTrunkNegLog10ScaleEngine();
  virtual void 	autoScale (int,double&,double&,double&) const;
  virtual QwtScaleTransformation *transformation() const;
  double minValue() const;
  void setMinValue(double);
};