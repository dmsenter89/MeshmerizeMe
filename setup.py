from setuptools import setup
import os
import sys
#from distutils.core import setup # distutils no longer recommended

setup(
    name='MeshmerizeMe',
    version='1.0.dev0',
    packages=['MeshmerizeMe', 'MeshmerizeMe.scripts'],
    entry_points={
        'console_scripts': [
            'MeshmerizeMe = MeshmerizeMe.scripts.MeshmerizeMe:main',
            'MMeSolveSVC = MeshmerizeMe.scripts.MMeSolveSVC:main',

            # These should be moved to gui_scripts if their logs should not be written to stdout.
            'ContourizeMe = MeshmerizeMe.scripts.ContourizeMe:main',
            'MMeSamplePixels = MeshmerizeMe.scripts.MMeSamplePixels:main',

            # Uncomment this line if MMePredictBinaryImage is a console_script
            #'MMePredictBinaryImage = MeshmerizeMe.scripts.MMePredictBinaryImage:main',
        ],

        # WARNING: gui_scripts cannot use stdin/stdout, so logs must be written to a file.
        # If we want logs to be written to a console, we must use the scripts as console_scripts instead.
        'gui_scripts': [
            # Uncomment this line if MMePredictBinaryImage is a gui_script, and its logs should not be written to stdout.
            #'MMePredictBinaryImage = MeshmerizeMe.scripts.MMePredictBinaryImage:main',
        ]
    },

    # dependencies
    install_requires=[
        "matplotlib >= 3.1.1",
        "multiprocess >= 0.70.8",
        "opencv-python >= 4.1.0.25",
        "pandas >= 0.15.2",
        "Pmw >= 2.0.1",
        "scikit-image",
        "scikit-learn",
        "svgpathtools",
        "tqdm >= 4.32.1",
    ],
    extras_require={
        'dev-tools':  ["Jinja2 >= 2.10.3"],
    },

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
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Multimedia :: Graphics',
                 'Topic :: Multimedia :: Graphics :: 2D Modeling',
                 'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
                 'Topic :: Multimedia :: Video',
                 'Topic :: Scientific/Engineering'],
)
