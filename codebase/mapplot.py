# -*- coding: utf-8 -*-
""" Plot the location map of the selected earthquake """
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from IPython.display import display, clear_output
import ipywidgets as widgets

def plot_map(raspberry):
    """ Plot the location map of the selected earthquake """
    # Get the selected earthquake
    selected = raspberry.get_selected_earthquake()
    
    # Make sure the output widget is created
    if raspberry.plot_output is None:
        raise ValueError("The output widget is not created")

    with raspberry.plot_output:
        clear_output()
        
        # Plot the map
        fig = plt.figure(figsize=(11, 11))

        # Setup projections depending on the region scale
        if raspberry.is_region_switzerland():
            projection = ccrs.AlbersEqualArea(central_longitude = 8.5, 
                                            central_latitude = 46.5)
            ax = fig.add_subplot(111, projection=projection)
            ax.set_extent((5.5, 11., 45.5, 48))
            ax.add_feature(cfeature.BORDERS)
            ax.add_feature(cfeature.LAKES, alpha=0.5)
            ax.add_feature(cfeature.RIVERS)
        else:
            projection = ccrs.PlateCarree()
            ax = fig.add_subplot(111, projection=projection)
        
            if raspberry.is_region_europe():
                ax.set_extent((45, -15, 70.,30))
            else:
                ax.set_extent((-180, 180., -90, 90))
            ax.stock_img()

        # Draw standard features
        ax.gridlines()
        ax.coastlines()
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
    
        plt.show()
