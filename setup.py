"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ["UnMixer.py"]
DATA_FILES = ["unmix.py", "lalalai_splitter.py"]
OPTIONS = {
    "iconfile": "support/unmixer.icns",
    "packages": ['tkinter'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
