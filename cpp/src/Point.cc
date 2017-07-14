/*!
 * @file Point.cc
 * @brief Implements the Point class with its methods.
 *
 * @author Michael Senter
 */

#include "Point.h"
#include <cmath>

Point::Point(){
    // empty
}

Point::Point(double xval, double yval){
    x = xval;
    y = yval;
}

/*!
 * @brief Allows printing of points in a standard
 * manner
 */
std::ostream &operator<<(std::ostream &os, const Point &p){
    os << p.x << " " << p.y;
    return os;
}

Point& Point::operator+=(const Point& rhs){
  x += rhs.x;
  y += rhs.y;
  return *this;
}

Point& Point::operator-=(const Point& rhs){
  x -= rhs.x;
  y -= rhs.y;
  return *this;
}

Point operator+(const Point& p1, const Point& p2){
  Point sum = p1;
  sum.x += p2.x;
  sum.y += p2.y;
  return sum;
}

Point operator-(const Point& p1, const Point& p2){
  Point diff = p1;
  diff.x -= p2.x;
  diff.y -= p2.y;
  return diff;
}

Point operator*(const double& k, const Point& p){
  Point multiple = p;
  multiple.x *= k;
  multiple.y *= k;
  return multiple;
}

Point operator*(const Point& p, const double& k){
  Point multiple = p;
  multiple.x *= k;
  multiple.y *= k;
  return multiple;
}

/*!
 * This function takes the power of a point element-wise.
 * @param  exp The exponent for the power operation.
 * @return     returns a Point.
 */
Point Point::pow(const double& exp){
  Point val = *this;
  val.x = std::pow(val.x, exp);
  val.y = std::pow(val.y, exp);
  return val;
}

/*!
 * Takes square-root of a point, element-wise.
 * @return Point that is the element-wise square-root.
 */
Point Point::sqrt(){
  Point val = *this;
  val.x = std::sqrt(val.x);
  val.y = std::sqrt(val.y);
  return val;
}

/*!
 * @brief: Find the Euclidean distance between the current point and p2.
 *
 * Finds the Euclidean distance between a Point p1 and p2 using the formula
 * \f[
 *  \sqrt{\left(p_{2,x}-p_{1,x}\right)^2 + \left(p_{2,y}-p_{1,y}\right)^2}.
 *  \f]
 * @param  p2 The second point for comparison.
 * @return    The Euclidean distance as double.
 */
double Point::distance(const Point& p2){
    double dx = p2.x-x;
    double dy = p2.y-y;
    return std::sqrt(std::pow(dx,2)+std::pow(dy,2));
}
