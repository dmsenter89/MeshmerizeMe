/*!
   \file Point.h
   \brief Contains the Point class, a basic class to represent a a point or
   vector in \f$\mathbb{R}^2\f$.

   \author Michael Senter
*/


#ifndef MESHME_POINT_H_
#define MESHME_POINT_H_

#include <iostream>

/*!
    @brief Point is a very simple class to represent points in \f$\mathbb{R}^2\f$.

    The class addition and compound addition/substraction operators defined.
    It includes functions to take powers and the square-root element-wise.
*/
class Point {
    friend std::ostream &operator<<(std::ostream &os, const Point &p);
    public:
        // constructors
        Point();
        Point(double, double y);
        // members
        double x; /*!< The \f$x\f$ coordinate of the Point.*/
        double y; /*!< The \f$y\f$ coordinate of the Point. */
        // operators
        Point& operator+=(const Point&);
        Point& operator-=(const Point&);
        // member functions
        Point pow(const double&);
        Point sqrt();
        double distance(const Point&);
};

Point operator+(const Point& p1, const Point& p2);
Point operator-(const Point& p1, const Point& p2);
Point operator*(const double& k, const Point& p);
Point operator*(const Point& p, const double& k);


#endif  // MESHME_POINT_H_
