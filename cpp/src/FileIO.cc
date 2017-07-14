/*!
 * @file FileIO.cc
 * @author Michael Senter
 */

#include "FileIO.h"
#include <iostream>
#include <cstring>
#include <string>
#include <fstream>
#include <iomanip>
#include <boost/property_tree/xml_parser.hpp>

#include "Curves.h"

using namespace std;
using boost::property_tree::ptree;


SvgFile::SvgFile(const std::string &fname){
    ptree pt;
    read_xml(fname, pt);    // initialize ptree to the xml, i.e. SVG file
    auto root_node = pt.get_child("svg");   // necessary to get main node
    map<string, string> root_attributes;
    for (auto &atts: root_node.get_child("<xmlattr>")){
        root_attributes[atts.first.data()] = atts.second.data();
    }
    this->file_dimension = extract_dimensions(root_attributes);
    this->geo_objects = parse_geo_objects(root_node);
}

SpaceDim SvgFile::get_space(){
    return this->file_dimension;
}

SpaceDim SvgFile::extract_dimensions(map<string, string> &attributes){
    auto myspace = SpaceDim();
    if (attributes.find("viewBox") != attributes.end()){
        string viewbox = attributes["viewBox"];
        myspace = SpaceDim(viewbox);
    } else if (attributes.find("height") != attributes.end()) {
        double ymax = stod(attributes["height"]);
        double xmax;
        if (attributes.find("width") != attributes.end()){
            xmax = stod(attributes["width"]);
        } else {
            xmax = ymax;
        }
        myspace = SpaceDim(xmax,ymax);
    } else if (attributes.find("width") != attributes.end()){
        double xmax = stod(attributes["width"]);
        double ymax = xmax;
        myspace = SpaceDim(xmax, ymax);
    }

    return myspace;
}


/*!
 * Function parses geometric objects that are "parsable" out of an SVG that has
 * been read into a property_tree. This function is intended for the constructor
 * of the SvgFile class.
 * @param  tree A ptree initialized with the `read_xml` function. Assumes that
 *              we have the tree starting from the <svg> node.
 * @return      Vector of SvgElem. All parsable elems are icnluded, with no
 *              distinction between type of SvgElem.
 */
std::vector<SvgElem> SvgFile::parse_geo_objects(ptree tree){
    vector<SvgElem> v;
    for (auto &child: tree){
        if (this->parsable.find(child.first)!=this->parsable.end()){
            // this means we know how to parse the object
            SvgElem thisElem;
            thisElem.name = child.first.data();
            map<string, string> attributes;
            for (auto &atts : child.second.get_child("<xmlattr>")){
                attributes[atts.first.data()] = atts.second.data();
            }
            thisElem.attr = attributes;
            v.push_back(thisElem);
        } else if (child.first == "g") {
            auto tempvec = parse_geo_objects(child.second);
            v.insert(v.end(), tempvec.begin(), tempvec.end());
        }
    }
    return v;
}


vector<Path> SvgFile::extractPathVec(){
  vector<Path> vPath;
  string pathString, tok="d";
  for (auto& path: geo_objects){
    pathString = path.attr[tok];
    auto tmpTok = tokenizeString(pathString);
    Path tmpPath(tmpTok);
    vPath.push_back(tmpPath);
  }
  return vPath;
}


/*!
 * @brief File to write a simple vertex file.
 *
 * @param fname. A string containing the absolute file path as well
 *               as the name of the file/experiment.
 * @param vPoints. A vector of points representing the mesh.
 *
 * @author Michael Senter.
 */
void writeVertex(std::string fname, std::vector<Point> &vPoints){
    ofstream fstrm(fname + ".vertex");

    fstrm << vPoints.size() << "\n"; // first line needs to have number of pts

    // set for preferred format of vertex files
    fstrm.precision(14);
    fstrm << scientific;

    // print all the points sequentially
    for (auto elem : vPoints){
        fstrm << elem << "\n";
    }

    fstrm.close();
}
