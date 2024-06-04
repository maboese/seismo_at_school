# -*- coding: utf-8 -*-
""" 
Plots vertical seismogram for all the stations for the selected earthquake.
"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from IPython.display import display, clear_output
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth
from codebase import config

def plot_all_seismograms(raspberry):
    # Use the seismogram plot output widget.
    with raspberry.seis_output:
        clear_output()

        
