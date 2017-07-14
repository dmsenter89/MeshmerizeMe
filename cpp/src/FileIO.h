/*!
 * @file FileIO.h
 *
 * This header groups together functions used in file i/o as it pertains
 * to reading SVG input files and writing the mesh.
 * @author Michael Senter
 */
#ifndef MESHME_FILEIO_H
#define MESHME_FILEIO_H

#include <string>
#include <vector>
#include <map>
#include <set>
#include <boost/property_tree/ptree.hpp>
#include "Point.h"
#include "Curves.h"

//std::vector<Path> extractPathsFromSvg(const std::string& fname);
void writeVertex(std::string fname, std::vector<Point> &vPoints);

struct SvgElem{
    std::string name;
    std::map<std::string, std::string> attr;
};

/**
 * @brief This class provides
 */
class SvgFile{
public:
    SvgFile() = default; // default constructor
    SvgFile(const std::string &fname);  // constructor, takes filename
    std::vector<SvgElem> geo_objects;   // holds the geometric objects
    std::vector<Path> extractPathVec();
    SpaceDim get_space();
private:
    std::set<std::string> parsable = {"path"};
    SpaceDim file_dimension; // holds the spacial dimensions of the file
    std::vector<SvgElem> parse_geo_objects(boost::property_tree::ptree tree);
    SpaceDim extract_dimensions(std::map<std::string, std::string> &attributes);
};

#endif  // MESHME_FILEIO_H
