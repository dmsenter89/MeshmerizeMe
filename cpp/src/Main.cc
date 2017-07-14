/*!
  \file Main.cc

  \brief This file includes the main function of the problem.
  \author Michael Senter
*/

/*! \mainpage MeshmerizeMe
 *
 * \section intro_sec Introduction
 *
 * This is an experimental build of core components of MeshmerizeMe, realized
 * in C++.
 *
 * \section install_sec Installation
 *
 * \subsection step1 Step 1: Pre-requisites
 * MeshmerizeMe requires a C++ compiler compatible with the C++11 standard. Aside
 * from the standard library, no other libraries are used.
 *
 * \subsection step2 Step 2: Make
 *  Just type `make` into your terminal from the build directory.
 * etc...
 */

#include <iostream>
#include <string>
#include <boost/algorithm/string.hpp>

#include "Token.h"
#include "Point.h"
#include "Curves.h"
#include "FileIO.h"

using namespace std;

// declaring included functions
void usage(void);
void process_file(const string& filename);

/*!
 * Main function of MeshmerizeMe. At this stage of development I mainly use it
 * to test various functions and settings.
 * @return int. Signals success or failure.
 */
int main(int argc, char const *argv[])
{
    if (argc==1){
      usage();
  } else if (argc>1) {
        string fname;
        for (int i = 1; i < argc; ++i) {
            fname = argv[i];
            process_file(fname);
        }
    }
    return 0;
}

void usage(void){
  string use;
  use = "Usage: meshmerizeme [fname]\n";
  use += "\nMeshmerizeMe is a piece of software to help you create geometries\n";
  use += "for IB2d.\n";
  cout << use;
}

void process_file(const string& filename){
    SvgFile myFile = SvgFile(filename);
    std::vector<SvgElem> all_paths = myFile.geo_objects;
    std::cout << "Found " << all_paths.size() << " paths in total.\n";
    std::cout << myFile.get_space() << std::endl;
}

/*!
 * @brief batch_process Function that iterates over stdin to process all SVGs
 * handed to it.
 *
 * The point of this function is to allow batch processing of SVGs supplied
 * by other unix files such as `find` and the like. It processes an instream
 * object which can either be stdin (default) or a file-stream provided by
 * the user.
 *
void batch_process_files(istream &strm=std::cin){
    std::string input_line;
    while(std::getline(strm, input_line)){
        // process each line assuming it is a file path.
        boost::trim(input_line);
        std::vector<Path> vPath = extractPathsFromSvg(input_line);
        // process all the things
    }
}
*/
