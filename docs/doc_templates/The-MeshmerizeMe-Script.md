# TL;DR
The software is a Python script and installs itself into the path. To create a mesh for the file simple.svg from inside its folder, simply use:
```bash
$ MeshmerizeMe.py simple.svg
```
That's it! Just make sure an input2d file is also present in the same folder as the SVG image. The input2d file uses the same syntax as IB2d and IBAMR. This file needs to reflect the settings of the simulation you are interested in running, specifically the domain size (Lx and Ly) and the number of Eulerian grid points (Nx and Ny). A minimal input2d file is provided in the repo. 

# Basic Usage - Command-line
```
{{ render_params["meshmerizeme_help_message"] }}
```

MeshmerizeMe has two main functions: creating vertex files (this is the default function) and plotting vertex files (you can enable this with the `-p` or `--plot` flag). The command is followed by one or more filenames, e.g.
```bash
$ MeshmerizeMe.py /home/user/test1/file1.svg /home/user/test2/file2.svg
```
and so forth. MeshmerizeMe also features a batch-processing mode. If the filenames are omitted it will read files from stdin instead. For example, if you have a text file called myfiles.txt which has multiple files and paths (1 per line), you can call MeshmerizeMe as follows:
```
$ MeshmerizeMe.py < myfiles.txt
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
{{ render_params["meshmerizeme_limitations"] }}
