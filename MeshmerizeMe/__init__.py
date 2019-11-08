#!/usr/bin/env python


import sys

from .version import __version__
from . import meshmerizeme_logger as logger

import platform
import matplotlib
if platform.system() == "Darwin":
    try:
        matplotlib.use("Qt5Agg")
    except:
        logger.warning("The Qt5Agg backend was not found for matplotlib, so some graphical features may not work properly. " \
                      + "Please see the MeshmerizeMe wiki on Github for more details.")
        matplotlib.use("TkAgg")
else:
    matplotlib.use("TkAgg")

from .geo_obj import *
from .tools import *

