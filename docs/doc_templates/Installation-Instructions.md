MeshmerizeMe was written for Python 3. Minimal installation requirements are included in `setup.py`. A `requirements.txt` is also provided for user convenience. The minimal package requirements are: opencv-python, pandas, Pmw, scikit-image and scikit-learn, svgpathtools, and tqdm. Note that it is **not** necessary to download and install opencv itself. The opencv-python package is shipped with the necessary binaries.

## Windows
It is recommended to use the Anaconda Python distribution available [here](https://www.anaconda.com/distribution/). Make sure to download the 3.x version, and not the 2.7 version. 

Once Anaconda has been installed and MeshmerizeMe downloaded, open an Anaconda prompt and navigate to the MeshmerizeMe folder which contains the `setup.py` file. The command `pip install .` executed here will install the software. Although MeshmerizeMe and ContourizeMe will only be available from the Anaconda prompt, the installation will only have to be executed once.

MeshmerizeMe can be uninstalled by running `pip uninstall MeshmerizeMe` from the Anaconda prompt.

## macOS \& Linux

Ensure that `pip` is available from the terminal. Then run `pip install .` from the MeshmerizeMe directory to install. Both the ContourizeMe and MeshmerizeMe scripts will be callable from the terminal thereafter.

MeshmerizeMe can be uninstalled by running `pip uninstall MeshmerizeMe` from the terminal.

### macOS
Some graphical features may not work properly by default on macOS. See [here](https://matplotlib.org/3.1.0/faq/osx_framework.html) for potential solutions.

We suggest using Anaconda with PyQt5 installed:
Create a new environment with `conda create -n <environment-name> python=3 pyqt=5` and activate it with `conda activate <environment-name>`. Then install and use MeshmerizeMe as normal.

## Troubleshooting

### Unable to install opencv-python with pip — "pip install" command is hanging
Try [these](https://stackoverflow.com/questions/45293933/could-not-find-a-version-that-satisfies-the-requirement-opencv-python) solutions:
- `pip install --upgrade pip && pip install opencv-python`
- If you are on Linux: `sudo apt-get install python-opencv`
- If you are using Anaconda: `conda install opencv`
- Downgrade Python to version 3.6
