# MeshmerizeMe (Python)
MeshmerizeMe is a python script intended to convert SVG files into
geometry files for use with IBAMR and IB2D. Also includes the ability to
plot .vertex files to verify the geometry looks as intended.

This version will only handle 2D code. See the project wiki for more
information.

## Input and Output
An SVG file with no grouping (<g> elements) and an input2d file for the
simulation. Outputs a .vertex file that can be plotted.

## Usage:
```
MeshmerizeMe.py [-h] [--gui] [-i | -p] [fname [fname ...]]

Welcome to MeshmerizeMe. MeshmerizeMe is a Python script intended to assist
with creating geometries for fluid simulations using IBAMR and IB2d. It uses a
user-supplied SVG file and input2d file to create .vertex files, and can plot
the same.

positional arguments:
  fname             Path to file(s) for processing. If omitted, program will
                    run in batch-processing mode.

optional arguments:
  -h, --help        show this help message and exit
  --gui             Start GUI mode. Ignores other parameters.
  -i, --input-file  Mesh SVG file(s). Default option. Exclusive with plot.
  -p, --plot        Plot existing .vertex file(s). Exclusive with input-file.

Note that the file argument is optional. If no file is specified on the
commandline the program will start in batch mode. If the user supplies the
path to one or more file(s) on the commandline, MeshmerizeMe will proceed to
process them.
```

## Requirements and Dependencies:
Python 3.x. PyQt5. Matlab. NumPy. [tqdm](https://pypi.python.org/pypi/tqdm). [svg.path](https://pypi.python.org/pypi/svg.path).

Installation on your local machine
==================================
Prerequisites
--------------
Windows (Vista, 7, 8.1, 10):
----------------------------

Download Python from https://www.python.org/downloads/

Don't click on either button at the top of the screen - these are links 32bit versions
* Select Python 2.7.11 (or higher numbered 2.7.xx) from the table
* Download the Windows x86-64 MSI installer
* Double-click the installer
* In the install options:
* Choose "Install for all users"
* Add Python.exe to path

Go to [http://www.lfd.uci.edu/~gohlke/pythonlibs/](Link URL)

**Version numbers may have changed (find the latest for Python 2.7)**

* Download numpy-1.10.4+mkl-cp27-cp27m-win_amd64.whl
* Download opencv_pythonâ€‘3.1.0â€‘cp27â€‘cp27mâ€‘win_amd64.whl
* Download matplotlib-1.5.1-cp27-none-win_amd64.whl
* Download scikit_imageâ€‘0.12.3â€‘cp27â€‘cp27mâ€‘win_amd64.whl

Due to a recent change since making the video tutorial, you must now install ffmpeg independently. Please follow the instructions at: http://www.wikihow.com/Install-FFmpeg-on-Windows.  Open an administrator cmd.exe session:

* Press the Windows key to bring up start menu (or click on it)
* Type in cmd
* Right-click on the "command prompt" start menu entry and select Run As Administrator

In the command prompt, type cd c:\Users\hedricklab\Downloads (substitute your username for hedricklab)
Run "pip install xx" where xx is each of the packages downloaded in step 2. Installation order matters slightly, use the order in Step 2 to be safe.

If you see the error "numpy-1.10.4+mkl-cp27-cp27m-win_amd64.whl is not a supported wheel on this platform." or similar try python -m pip install --upgrade pip from the command prompt - this will upgrade pip. After that finishes, try the failed install again.

Ubuntu
-------

Setup a python2.7 environment using the Ubuntu package repository & easy_install.
    
    # pre reqs for OpenCV
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install build-essential cmake git pkg-config
    sudo apt-get install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev
    sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk2.0-dev libatlas-base-dev gfortran

    # python stuff
    sudo apt-get install python2.7 python-setuptools python2.7-dev libatlas-base-dev gfortran g++
    sudo easy_install pip
    sudo easy_install numpy
    sudo easy_install scikit-image
    sudo apt-get install python-matplotlib


Get opencv and opencv_contrib from the following repositories: https://github.com/Itseez/opencv,  https://github.com/itseez/opencv_contrib

Extract them as opencv and opencv_contrib to your home folder.
Run:

	cd ~/opencv
	mkdir build
	cd build
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_C_EXAMPLES=ON \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	-D BUILD_EXAMPLES=ON ..
	sudo make -j4
	sudo make install

Mac OS
------

Install the brew package manager

Run the following command in terminal:
	
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

Install the Command Line Tools (CLT) from the Xcode suite or Apple's website

MacOS 10.11 & 10.12 had the CLT installed during the brew setup in step 1
MacOS 10.9+ have the CLT available through Apple's software update
MacOS 10.8 users should download a disk image and install it
This script automates either process: [https://github.com/rtrouton/rtrouton_scripts/tree/master/rtrouton_scripts/install_xcode_command_line_tools](Link URL) \n

* Visit the page
* View the script
* Click the "copy path" button
* run "sudo bash" in a terminal prompt
* use Edit --> Paste to run the script

Install Python 2.7.x, and make some additions then install ffmpeg and hdf5:

	brew install python
	brew linkapps python
	brew tap homebrew/science
	brew install libhdf5-dev
	brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-libass --with-libquvi --with-libvorbis --with-libvpx --with-opus --with-x265

Install opencv3 - use [Method 1] for an easy and fast(er) install OR [Method 2] to build from source

[Method 1] Instructions from this website, summarized and simplified below.

	 brew install opencv3 --with-contrib --with-python --with-ffmpeg --HEAD

[Method 2] To install from source, install requisites as per this website (http://www.pyimagesearch.com/2015/06/15/install-opencv-3-0-and-python-2-7-on-osx/)
Download the latest opencv and opencv-contrib
Make the build folder within opencv and cd into it
Run:

	cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local \
	-D PYTHON2_PACKAGES_PATH=~/.virtualenvs/cv/lib/python2.7/site-packages \
	-D PYTHON2_LIBRARY=/usr/local/Cellar/python/2.7.10/Frameworks/Python.framework/Versions/2.7/bin \
	-D PYTHON2_INCLUDE_DIR=/usr/local/Frameworks/Python.framework/Headers \
	-D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON \
	-D BUILD_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules ..
	make -j4
	sudo make install


