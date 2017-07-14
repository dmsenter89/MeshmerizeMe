/*!
 * @file Token.h
 * @brief Represents the Token class used to turn a path data string into a
 * sequence of Tokens for processing.
 * @author Michael Senter
 */

#ifndef MESHME_TOKEN_H_
#define MESHME_TOKEN_H_

#include <vector>
#include <string>


/*!
 * This class represents a Token.
 */
class Token {
    public:
        // some constructors
        Token();
        Token(char letter);
        Token(char, std::vector<double>);

        // member functions
        char type;  /*!< type represents a command character used by
                        SVG to represent a curve/line, for example
                        'M' (move-to) or 'L' (line-to). */
        std::string coords; /*!< This string holds the coordinates relevant
                            to the command held in type.*/
        std::vector<double> coordPts; /*! List of coordinate points.*/
};

std::vector<Token> tokenizeString(std::string const& rpd);
int getNumOfExpectedCoordinates(const char& letter);
#endif  // MESHME_TOKEN_H_
