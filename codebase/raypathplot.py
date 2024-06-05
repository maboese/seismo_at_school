import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, clear_output
import obspy
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth
from codebase import config
from codebase.seisplot import get_waveforms

# The phases to include in the plot
phase_list = ['p', 'P', 'PP', 's', 'S', 'SS']

def plot_ray_paths(raspberry):
    """ Plot the ray paths of the selected seismic phases."""
    with raspberry.seis_output:
        clear_output(wait=True)

        selected_eq = raspberry.get_earthquake_quakeml()
        eq_depth = selected_eq.origins[0].depth / 1000.0
        eq_lon = selected_eq.origins[0].longitude
        eq_lat = selected_eq.origins[0].latitude

        selected_sta = raspberry.get_selected_station_inventory()
        sta_lon = selected_sta[0][0].longitude
        sta_lat = selected_sta[0][0].latitude

        distance, _, _ = gps2dist_azimuth(eq_lat, eq_lon, sta_lat, sta_lon)
        distance = distance / 1000.0
        # Convert km to degrees
        distance_in_deg = distance / 111.0

        if eq_depth < 0:
            eq_depth = 1.0

        # The coordinate frame for the plot
        if raspberry.is_region_worldwide():
            plot_type = 'spherical'
        else:
            plot_type = 'cartesian'
            
        model = TauPyModel(model="iasp91")
        arrivals = model.get_ray_paths(source_depth_in_km=eq_depth, 
                                       distance_in_degree=distance_in_deg,
                                       phase_list=phase_list)
        
        arrivals.plot_rays(plot_type=plot_type, legend=True, show=False)

        plt.savefig("ray_paths.png")
        plt.show()

