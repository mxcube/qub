#include<vector>
#include <list>

class Polygone
{
 public:
  struct Point
  {
    double x;
    double y;
  };
  static void points_inclusion(const std::vector<Point> &Points,
			       const std::vector<Point> &PointsPolygone,
			       std::list<int> &aResultList,bool winding = false);
};
