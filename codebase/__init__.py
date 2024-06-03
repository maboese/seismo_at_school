# __init__.py for the codebase subpackage
# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings('ignore')
import subprocess
import pkg_resources
import sys

print("Checking for the required libraries...")
essential_libraries = ['obspy', 'cartopy', 'matplotlib', 'ipywidgets', 'numpy']
for library in essential_libraries:
    try:
        __import__(library)
        print(f"{library} satisfies the requirements")
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', library])
        print(f"{library} is now installed and imported successfully")

# Explicit imports to make sure they are available when the package is imported
import obspy
import cartopy
import matplotlib
import ipywidgets
import numpy

# Additional imports required for the notebook
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime, Stream, Trace, Stats
from obspy.taup import TauPyModel
from obspy.geodetics import gps2dist_azimuth
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from ipywidgets import widgets, interact, Dropdown, Select

print("All required libraries are installed and imported.")

# GUI imports
from codebase.gui import RaspberryShake
