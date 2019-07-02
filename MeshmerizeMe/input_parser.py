#!/usr/bin/python
# -*- coding: utf-8 -*-

def fetch_input_params(fname, params={}):
    """ Read in function parameters from input2d file at fname.

    Parses the input2d file line by line, and adds the parameters to a
    dictionary file. Order of parameters is irrelevant, but they have to be give
    in such a way that the line will split into at least three arguments, with
    keyword being in the first position and its value at the third position.

    Args:
        - fname: path to input2d file. Required.
        - params: dictionary to append parameters to. optional.

    Returns:
        - params: dictionary containing all the parameters given in
                    the input2d file.
    """
    with open(fname) as inFile:
        for line in inFile:
            if (line[0].isalpha()) and ('=' in line):
                parts = line.split()
                if parts[0]=="string_name":
                    params[parts[0]] = parts[2].strip('"')
                else:
                    try:
                        params[parts[0]] = float(parts[2])
                    except:
                        params[parts[0]] = parts[2]
    params['Ds'] = 0.5*params['Lx']/params['Nx'] # ideal distance between
                                                 # Lagrangian pts
    return params

def print_params(dic):
    """ Print the parameters that were read.
    """
    for k, v in list(dic.items()):
        print((k, '-->', v, ' ({})'.format(type(v))))

def test():
    # test function requires input2d to be in same folder.
    pdict = fetch_input_params('input2d')
    print_params(pdict)

if __name__ == '__main__': test()
