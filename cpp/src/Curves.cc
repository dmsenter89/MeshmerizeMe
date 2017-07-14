/*!
 * @file Curves.cc
 * @brief The implementation of the BezierCurve class with its methods.
 *
 * @author Michael Senter
*/

#include "Curves.h"
#include <iostream>
#include <regex>
#include <cmath>
#include <cctype>
#include <sstream>

using namespace std;

/**
 * @brief Constructor creates a space from a string.
 *
 * The correct format for the viewBox string is as follows:
 *  "xmin ymin xmax ymax"
 * It consists of four doubles.
 *
 * @param viewBoxString This string represents the viewBox string
 *              given in the SVG standard.
 */
SpaceDim::SpaceDim(string viewBoxString)
{
    // stuff to do
    stringstream strm(viewBoxString);
    strm >> xmin;
    strm >> ymin;
    strm >> xmax;
    strm >> ymax;
}


std::ostream &operator<<(std::ostream &os, const SpaceDim &s){
    os << s.xmin << " " << s.ymin << " "
       << s.xmax << " " << s.ymax;
    return os;
}

/**
 *  The preferred way to initialize a BezierCurve at the moment.
 *
 * This function creates a single Bezier curve from a Token. It translates the
 * token into a vector of control points, and sets the degree of the Bezier curve.
 *
 * @param tok. A Token representing the control point coordinates of a BezierCurve.
*/
BezierCurve::BezierCurve(Token tok) {
    ctrlPoints = createPoints(tok);
    n = ctrlPoints.size()-1;
}


/**
 * @brief Initializes a BezierCurve object based on vector of its control points. This
 * is the preferred method for initialization.
 * @param rvec A STL vector of the control Points for the curve.l
 */
BezierCurve::BezierCurve(std::vector<Point> rvec){
    ctrlPoints = rvec;
    n = ctrlPoints.size()-1;
}


/*!
 * @brief Uses regex to parse a token string for control points.
 *
 * This function is called by the constructor to set up a Bezier curve. It
 * operates under the assumption that we are creating a curve in two dimensions.
 *
 * @param tok. A constant reference to a token.
 * @return A vector of control Points.
 * @author Michael Senter
 */
vector<Point> BezierCurve::createPoints(const Token&  tok){
    vector<Point> vec;
    if ((tok.type != 'Z')||(tok.type != 'z')){
      for (auto p=tok.coordPts.begin(); p!=tok.coordPts.end();++p){
        Point pt;
        pt.x = *p;
        ++p;
        pt.y = *p;
        vec.push_back(pt);
      }
    } else {
      Point pt;
      pt.x = 0.0;
      pt.y = 0.0;
      vec.push_back(pt);
    }
    return vec;
}


/*!
 * @brief evaluates the Bezier curve at point \f$t\in[0,1]\f$.
 *
 * @param double t, with value in the interval [0,1].
 * @warning Function does  \e not currently check whether or not the input
 * is in a valid range. If input is not in valid range, result will be meaningless.
 * @return Point corresponding to t.
 * @author Michael Senter
*/
Point BezierCurve::eval(double t)
{
    Point ans;
    vector<Point> vec = ctrlPoints;
    for (int j=1; j<=n ; ++j) {
        for (int  i=0; i<=(n-j); ++i) {
            vec[i].x = vec[i].x*(1-t)+vec[i+1].x*t;
            vec[i].y = vec[i].y*(1-t)+vec[i+1].y*t;
        }
    }
    ans = vec[0];
    return ans;
}


/*!
 * Function calculates the length of the given BezierCurve object.
 *
 * The integral giving the arc length of a BezierCurve is given be
 * \f[
 *  \int_0^1 \sqrt{[B_x'(t)]^2+[B_y'(t)]^2} dt.
 *  \f]
 *  We use a Gaussian quadrature of order three to evaluate this integral, giving
 *  us accuracy up to the order \f$t^5\f$ term in the Taylor expansion of the
 *  integrand. Letting
 *  \f[ f(t)=[B_x'(t)]^2+[B_y'(t)]^2 \f]
 *  our quadrature takes the form
 *  \f[
 *  \int_0^1 f(t) dt = \frac{1}{18} \left[5 f\left(\frac{1}{2} - \frac 12
 *  \sqrt{\frac 35} \right) + 8 f \left (\frac 12 \right)+
 *  5 f\left( \frac 12 + \frac 12 \sqrt{\frac 35}\right)\right]
 *  \f]
 * @return the length of the BezierCurve.
 * @author Michael Senter
 */
double BezierCurve::getArcLength() {
    double length=-1;
    if(n>1){
        double  t0 = 0.5*(1-std::sqrt(3.0/5.0)), // first eval node
                t1 = 0.5,               // second eval node
                t2 = 0.5*(1+std::sqrt(3.0/5.0)); // third eval node

        // evaluate f(t0), f(t1), f(t2)
        // create the derivative curve we will use
        vector<Point> vecQ(n);
        for (auto i=0; i<n; ++i){
            vecQ[i] = ctrlPoints[i+1]-ctrlPoints[i];
        }
        auto Q = BezierCurve(vecQ);

        // Calculate the derivative points
        Point p0 = n*Q.eval(t0),
              p1 = n*Q.eval(t1),
              p2 = n*Q.eval(t2);

        // evaluate f(t) = sqrt(B'_x^2 + B'_y^2)
        double f0 = std::sqrt(std::pow(p0.x,2)+std::pow(p0.y,2)),
               f1 = std::sqrt(std::pow(p1.x,2)+std::pow(p1.y,2)),
               f2 = std::sqrt(std::pow(p2.x,2)+std::pow(p2.y,2));

        length = 5*f0 + 8*f1 + 5*f2;
        length *= 1.0/18.0;
    } else {
        length = ctrlPoints[0].distance(ctrlPoints[1]);
    }
    return length;
}

/*!
 * @brief Evaluates Bernstein basis polynomial.
 *
 * A Bernstein basis polynomial is defined as
 * \f[
 *   b_{i,n} (t)= \binom{n}{i} (1-t)^{n-i} t^i.
 * \f]
 * @param  i integer index.
 * @param  n integer index.
 * @param  t argument of polynomial. For Bezier Curves, we require that
 *           \f$ t\in[0,1]\f$.
 * @return double representing the evaluation of the Bernstein basis at t.
 */
double evalBernsteinBasis(int& i, int& n, double& t){
  // pass; lines only here to supress compiler warnings.
  double someval{3.14};
  return someval;
}


/*!
 * The "main" constructor of the Path class. It takes a Token vector, created by
 * the Token class, and iterates over it to create a vector of BezierCurve
 * objects. A standard space is added to it. This is likely not the ideal constructor
 * to use.
 *
 * @author Michael Senter
 */
Path::Path(std::vector<Token> &rvecTok){
    mCurves = createBCurveVector(rvecTok);
    mSpace = SpaceDim();
}


Path::Path(std::vector<Token> &rvecTok, SpaceDim space){
    mCurves = createBCurveVector(rvecTok);
    mSpace = space;
}


/**
 * @brief Function that iterates over Token objects and constructs a
 *        vector of curves from it.
 * @param rvecTok
 * @return
 */
vector<BezierCurve> Path::createBCurveVector(vector<Token> &rvecTok){
    // these are points we need to track
    Point startPoint(-999,-999), currPoint(-999,-999);
    double px, py;
    Point newPoint;
    std::vector<Point> vecPoints;
    std::vector<BezierCurve> vecCurves;
    // iterate over all the tokens
    auto it=rvecTok.begin();
    while (it != rvecTok.end()){
        // do stuff
        char currType = it->type;
        // distinguish between absolute and relative commands:
        if (currType=='M' || currType=='m'){
            // WARNING: pretends absolute coordinates are given
            startPoint.x = it->coordPts[0];
            startPoint.y = it->coordPts[1];
            vecPoints.push_back(startPoint);
        } else {
            if (isupper(currType)){
                // we have an absolute command
                switch (currType) {
                    case 'M':
                        // px = it->coordPts[0];
                        // py = it->coordPts[1];
                        startPoint.x = it->coordPts[0];
                        startPoint.y = it->coordPts[1];
                        vecPoints.push_back(startPoint);
                        break;
                    case 'H':
                        newPoint.x = it->coordPts[0];
                        newPoint.y = currPoint.y;
                        vecPoints.push_back(newPoint);
                        break;
                    case 'V':
                        newPoint.x = currPoint.x;
                        newPoint.y = it->coordPts[0];
                        vecPoints.push_back(newPoint);
                        break;
                    case 'Z':
                        newPoint.x = startPoint.x;
                        newPoint.y = startPoint.y;
                        vecPoints.push_back(newPoint);
                        break;
                    case 'A':
                        std::cout << "Can't handle arcs." << std::endl;
                        break;
                    default:
                    //these all come in pairs. iterate over them to fill the curve.
                        if (currType=='S'||currType=='T'){
                            // these are smooth types of curves, so we have to
                            // repeat the last points
                            vecPoints.push_back(currPoint);
                        }
                        auto locit = (it->coordPts).begin();
                        auto itends = (it->coordPts).end();
                        while (locit != itends){
                            newPoint.x = *locit;
                            newPoint.y = *(locit+1);
                            locit += 2;
                            // Point newPoint(px,py);
                            vecPoints.push_back(newPoint);
                        }
                        break;
                }
                currPoint = vecPoints.back();
                BezierCurve newCurve(vecPoints); // creates the curve
                vecCurves.push_back(newCurve);  // and appends
                vecPoints.clear();
                vecPoints.push_back(currPoint); // for continuity purposes
            } else {
                // we have a relative command
                px = 0;
                py = 0;
            }
        }
    ++it;
    }
    // at the end, set vector of curves.
    return vecCurves;
}


/*!
 * @brief This function creates a mesh consisting of points that
 * have a curvilinear distance of ds.
 *
 * @param ds. The desired distance of points.
 */
vector<Point> Path::mesh(double ds){
    std::vector<Point> vPt;
    bool startPoint=true;
    // TODO: this actually works provided the Path object is not closed.
    // If the path object IS closed however, the first and last point will
    // be generated twice, which seems undesirable. One option to handle that
    // would be to include a function/member-var for Path that checks if the
    // path is closed (true if the first control point of the first curve is
    // equal to the last control point of the last curve. If the query for
    // closed-ness returns true, we iterate over the meshes and never generate
    // the first point. If it is false, we generate the start point for the first
    // curve only as is done here.
    for (auto curve : mCurves){
        curve.mesh(vPt, ds, startPoint);
    }
    return vPt;
}

/*!
 * @brief This helper function creates a mesh from a BezierCurve; it is used
 * by the Path's member function of the same name.
 */
void BezierCurve::mesh(std::vector<Point> &rvPt, const double &ds, bool startPoint){
    int i;  // this will be the counting variable
    double t; // and this will be the point we evaluate in [0,1]

    // define if we start at i=0 or i=1, which depends on whether or not
    // we will be including the endpoint
    if (startPoint)
        i=0;
    else
        i=1;

    // decide how many points we need to sample for the desired spacing
    auto m = getArcLength()/ds;
    while (i<=m){
        t = (double) i/m;
        rvPt.push_back(eval(t));
        ++i;
    }
}
