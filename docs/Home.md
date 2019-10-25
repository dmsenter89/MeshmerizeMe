Welcome to the MeshmerizeMe wiki!

# Summary 
MeshmerizeMe is a software for the creation of 2D geometry files for use with [IB2d](https://github.com/nickabattista/IB2d) and [IBAMR](https://github.com/IBAMR/IBAMR). The software comes with two main scripts that will be installed into your system's path:

- ContourizeMe: provides a graphical interface to automatically extract contours from an image into an SVG file based on adjustable parameters.
- MeshmerizeMe: creates *.vertex files describing the geometry of SVG images at the appropriate resolution according to an IB2d style `input2d` file. This script can also plot the resulting vertices for visual verification of their accuracy.

## Usage:
To convert image files into the intermediate SVG format, call the 
`ContourizeMe` script. It will start a GUI for extracting contours. 

```
usage: ContourizeMe [-h] image

allows the user to slide to a values for 8-bit pixel thresholding

positional arguments:
  image

optional arguments:
  -h, --help  show this help message and exit

```

Call the `MeshmerizeMe` script to mesh the resulting SVG files.

```
usage: MeshmerizeMe [-h] [-p] [--subpath-length SUBPATH_LENGTH]
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
  -p, --plot            Plot existing .vertex file(s). (default: False)
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