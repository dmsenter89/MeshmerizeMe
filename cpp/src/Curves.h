 /*!
    \file Curves.h
    \brief Contains files to handle basic curve geometry.

    \author Michael Senter
*/

#ifndef MESHME_CURVES_H_
#define MESHME_CURVES_H_

#include <vector>
#include <string>
#include "Token.h"
#include "Point.h"


/*!
 * \brief The SpaceDim struct handles spacial dimension tracking by providing
 * convenient access points.
 */
struct SpaceDim {
    double xmin, xmax;
    double ymin, ymax;

    // Constructors
    SpaceDim(double a=1): xmin(0), xmax(a), ymin(0), ymax(a){}
    SpaceDim(double a, double b): xmin(0), xmax(a), ymin(0), ymax(b){}
    SpaceDim(double a, double b, double c, double d): xmin(a), ymin(b),
                                                      xmax(c), ymax(d) {}
    SpaceDim(std::string viewBoxString);
    friend std::ostream &operator<<(std::ostream &os, const SpaceDim &s);

};

/*!
    This class represents an \f$ n \f$-th degree Bezier curve.

    The class represents an arbitrary degree Bezier curve in \f$\mathbb{R}^2\f$
    by means of a vector of control points. The curve can be created and evaluated
    at any point \f$t\in[0,1]\f$.

    @author Michael Senter
*/
class BezierCurve {
    public:
        // setting up the constructors
        BezierCurve();
        BezierCurve(Token tok);
        BezierCurve(std::vector<Point>);
        // member functions
        Point eval(double);
        double getArcLength();
        int degree() const {return n;}
        void mesh(std::vector<Point> &rvPt, const double &ds, bool startPoint=true);

    private:
        std::vector<Point> createPoints(const Token&);
        std::vector<Point> ctrlPoints;
        int n;  /*!< Represents the degree of the Bezier curve.*/
};

double evalBernsteinBasis(int& i, int& n, double& t);



/*!
 * @brief: Class that represents an SVG path.
 *
 * This class implements a complete SVG path as a sequence of BezierCurve objects,
 * held in a vector.
 */
class Path{
    public:
        // constructors
        Path();
        Path(std::vector<Token> &rvecTok);
        Path(std::vector<Token> &rvecTok, SpaceDim space);
        // member functions
        std::vector<Point> mesh(double ds);
    // private:
        std::vector<BezierCurve> createBCurveVector(std::vector<Token> &rvecTok);
        std::vector<BezierCurve> mCurves; /**< Vector of BezierCurves in the path object.*/
        SpaceDim mSpace; /**< Represents the space in which the path lives.*/
};


#endif  // MESHME_CURVES_H_
