from setuptools import setup
import os
import sys
#from distutils.core import setup # distutils no longer recommended

setup(
    name='MeshmerizeMe',
    version='1.0.dev0',
    packages=['MeshmerizeMe'],
    scripts=['MeshmerizeMe/scripts/MeshmerizeMe', 'MeshmerizeMe/scripts/ContourizeMe'],
    # dependencies
    install_requires=[
        "numpy >= 1.9.1",
        "pandas >= 0.15.2",
        "matplotlib >= 1.3.1",
        "future >= 0.16.0",
        "svgpathtools",
        "svgwrite",
        "scipy",
        "scikit-image",
        "scikit-learn",
        "opencv-python >= 4.1.0.25",
        ],

    author='Michael Senter, Dylan Ray, and Steven Thomas',
    author_email='dmsenter@live.unc.edu',
    description='MeshmerizeMe is a Python script intended to convert SVG files into geometry files for use with IBAMR and IB2D. Also includes the ability to plot .vertex files to verify the geometry looks as intended.',
    license='GNU GPLv3',
    keywords='immersed boundary, mesh, computer vision',
    url='https://dmsenter89.github.io/project/meshmerizeme/',
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Operating System :: OS Independent',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Multimedia :: Graphics',
                 'Topic :: Multimedia :: Graphics :: 2D Modeling',
                 'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
                 'Topic :: Multimedia :: Video',
                 'Topic :: Scientific/Engineering'],
)
