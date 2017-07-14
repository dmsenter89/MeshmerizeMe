/*!
 * @file Token.cc
 * @author Michael Senter
 */

#include "Token.h"
#include <stdexcept>
#include <regex>
#include <iostream>
#include <boost/algorithm/string.hpp>


using namespace std;

Token::Token(){
  type = ' ';
}

Token::Token(char letter){
  type = letter;
}

Token::Token(char letter, std::vector<double> vec) {
    type = letter;
    coordPts = vec;
}

/*!
 * @brief Function that creates a vector of tokens out of a path data string.
 * @param string const& pd. This a path data string.
 * @return a vector consisting of Token objects. These tokens represent pairs of
 * command letters and coordinate strings.
 *
 * @author Michael Senter
 */
vector<Token> tokenizeString(string const& pd){
    vector<Token> v1;
    Token t;

    // this regex pattern matches ANY alpha as a command, even if that letter
    // wouldn't be in the command set as defined by the SVG standard.
    regex pat{ R"(([[:alpha:]]{1})([^[:alpha:]]*))" };

    for (sregex_iterator p(pd.begin(), pd.end(), pat); p!=sregex_iterator{}; ++p)
    {
        smatch m = *p; // not strictly necessary, but makes things more readable
        char command = (m.str(1)).c_str()[0];  // the command letter
        string str = m.str(2);    // a string with the coordinates
        boost::trim_right(str);   // gets rid of trailing whitespace
        vector<string> res;       // we'll create a string of the digits
        boost::split(res, str, boost::is_any_of(",, "));
        if ((command == 'Z')||(command == 'z')){
          Token myToken(command);  // doesn't take coordinates
          v1.push_back(myToken);
        } else {
          int num = getNumOfExpectedCoordinates(command);
          if ((res.size()%num)!=0){
              //throw std::invalid_argument("Wrong number of elements.");
              cout << "PROBLEM!!! WRONG NUMBER OF ELEMENTS! ";
          }
          auto index = 0;
          while (index < res.size()){
            // This loop handles implicit commands.
            vector<double> vec_coordinates;
            for (auto i=0; i<num; ++i){
              vec_coordinates.push_back(stod(res[index+i]));
            }
            Token myToken(command, vec_coordinates);
            index += num;
            v1.push_back(myToken);
          }
        }
    }
    return v1;
}

int getNumOfExpectedCoordinates(const char& letter){
  int ans = -1;
  switch (letter){
    case 'Z':
    case 'z':
        ans = 0;
        break;
    case 'H':
    case 'h':
    case 'V':
    case 'v':
        ans = 1;
        break;
    case 'M':
    case 'm':
    case 'L':
    case 'l':
    case 'T':
    case 't':
        ans = 2;
        break;

    case 'S':
    case 's':
    case 'Q':
    case 'q':
        ans = 4;
        break;
    case 'C':
    case 'c':
        ans = 6;
        break;
    default:
        throw std::invalid_argument("Unknown or not implemented token.");
        break;
  }
  return ans;
}
