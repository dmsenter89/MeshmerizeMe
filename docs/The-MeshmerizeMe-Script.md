# TL;DR
The software is a Python script and installs itself into the path. To create a mesh for the file simple.svg from inside its folder, simply use:
```bash
$ MeshmerizeMe.py simple.svg
```
That's it! Just make sure an input2d file is also present in the same folder as the SVG image. The input2d file uses the same syntax as IB2d and IBAMR. This file needs to reflect the settings of the simulation you are interested in running, specifically the domain size (Lx and Ly) and the number of Eulerian grid points (Nx and Ny). A minimal input2d file is provided in the repo. 

# Basic Usage - Command-line
```
usage: MeshmerizeMe [-h] [-i | -p] [--subpath-length SUBPATH_LENGTH]
                    [--num-points NUM_POINTS] [--learning-rate LEARNING_RATE]
                    [--max-iter MAX_ITER] [--threshold THRESHOLD]
                    [--show-graph]
                    [--num-parallel-processes NUM_PARALLEL_PROCESSES]
                    [fname [fname ...]]

Welcome to MeshmerizeMe. MeshmerizeMe is a Python script intended to assist
with creating geometries for fluid simulations using IBAMR and IB2d. It uses a
user-supplied SVG file and input2d file to create .vertex files, and can plot
the same. MeshmerizeMe uses the 'gradient descent' algorithm to minimize the
relative error of distances between points. First, the path is split into
multiple segments which are estimated in parallel. Then, the resulting points
are used as initial estimates for the final aggregate minimization.

positional arguments:
  fname                 Path to file(s) for processing. If omitted, program
                        will run in batch-processing mode. (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -i, --input-file      Mesh SVG file(s). Default option. Exclusive with plot.
                        (default: True)
  -p, --plot            Plot existing .vertex file(s). Exclusive with input-
                        file. (default: False)
  --subpath-length SUBPATH_LENGTH
                        Length of subpaths to estimate in parallel in terms of
                        ds. (default: 25)
  --num-points NUM_POINTS
                        Number of points to fit to the path. Leave this blank
                        to let the script automatically determine a value.
                        (default: None)
  --learning-rate LEARNING_RATE
                        The learning rate used by the gradient descent
                        algorithm for the final aggregate minimization over
                        the entire path. (default: 5e-05)
  --max-iter MAX_ITER   Maximum number of gradient descent iterations for the
                        final aggregate minimization over the entire path.
                        (default: 50)
  --threshold THRESHOLD
                        Stop the gradient descent process if the mean squared
                        error of point distances converges within the
                        threshold. (default: 1e-06)
  --show-graph          Flag to display/hide real-time graphs (for the final
                        aggregate minimization) containing: Histogram of point
                        parameters T; Mean squared error of point distances;
                        Plot of the estimated points. (default: False)
  --num-parallel-processes NUM_PARALLEL_PROCESSES
                        Number of processes to estimate subpaths in parallel.
                        (default: 10)

Note that the file argument is optional. If no file is specified on the
commandline the program will start in batch mode. If the user supplies the
path to one or more file(s) on the commandline, MeshmerizeMe will proceed to
process them.

```

MeshmerizeMe has two main command-line switches: `-i` or `--input-file` and `-p` or `--plot`. If neither is supplied, MeshmerizeMe will assume that you wanted `-i`. The switch is followed by one or more filenames, e.g.
```bash
$ MeshmerizeMe.py -i /home/user/test1/file1.svg /home/user/test2/file2.svg
```
and so forth. MeshmerizeMe also features a batch-processing mode. If the filenames are omitted it will read files from stdin instead. For example, if you have a text file called myfiles.txt which has multiple files and paths (1 per line), you can call MeshmerizeMe as follows:
```
$ MeshmerizeMe.py -i < myfiles.txt
```
Both modes function the same if the plotting option (`-p`) is specified. There's only one difference in plotting: if you specify the filenames on the command-line, each plot will be displayed. If you use batch-processing, the plots will be written to a png-file in the same folder as the .vertex files you plotted.

# Some Notes
Either give MeshmerizeMe *absolute paths* or paths that are relative to MeshmerizeMe, in which case you want to run the script from the folder in which you have stored the program. 

The script assumes that each svg or vertex file is provided with an input2d, and the output (the .vertex file) will be named after the `string_name` variable in the input2d file. That means that if you have two (or more) svgs that are similar and use the same input2d file, you need to have them in separate folders or the vertex file will be overwritten each time a new SVG is processed. In other words, if your folder looks like this:
```
$ ls
file1.svg file2.svg input2d
```
then after running MeshmerizeMe you would only have *one* .vertex file. Instead, you'd want it to look like this:
```
$ tree
.
├── experiment1
│   ├── file1.svg
│   └── input2d
└── experiment2
    ├── file2.svg
    └── input2d

2 directories, 4 files
```

# Creating a File for Batch Processing
For batch processing, you should generate a file with absolute paths. Suppose you have several folders with svg files in `/home/yourusername/research`. I would recommend the following commands to generate the file:
```
$ cd ~/research/
$ find $PWD -iname "*svg" > /path/to/MeshmerizeMe/myexperiments.txt
```
You can verify that the paths look correct:
```
$ cat /path/to/MeshmerizeMe/myexperiments.txt
/home/yourusername/research/experiment2/file2.svg
/home/yourusername/research/experiment4/file4.svg
/home/yourusername/research/experiment3/file3.svg
/home/yourusername/research/experiment1/file1.svg
```
Then all you need to do to run the experiments is this:
```
$ cd /path/to/MeshmerizeMe/
$ MeshmerizeMe < myexperiments.txt
```

# Limitations

MeshmerizeMe does not currently support SVG files containing any of the following:
- Nested viewBoxes/viewPorts
- Nested `<svg>` elements
- Use of the "preserveAspectRatio" attribute
- Use of units other than pixels
- `<use>`, `<symbol>`, and `<def>` tags
