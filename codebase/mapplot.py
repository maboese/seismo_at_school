# -*- coding: utf-8 -*-
""" 
Plots the location map of the selected earthquake. The event can be 
reached by the RaspberryShake object, which is the collection of 
widgets shown in the notebook.
"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from IPython.display import display, clear_output

def plot_map(raspberry):
    # Get the selected earthquake
    selected_eq  = raspberry.get_earthquake_quakeml()
    lon = selected_eq.origins[0].longitude
    lat = selected_eq.origins[0].latitude
    mag = selected_eq.magnitudes[0].mag
    depth = selected_eq.origins[0].depth / 1000.0
    time = selected_eq.origins[0].time

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

        # Plot the earthquake location
        ax.plot(lon, lat, 'ro', markersize=14, transform=ccrs.Geodetic())
        ax.text(lon, lat, f"M{mag:.1f}", transform=ccrs.Geodetic(), fontweight='bold',
                fontsize=14, verticalalignment='bottom', horizontalalignment='right')
        
        # selected station name
        selected_sta_code = raspberry.get_selected_station().split(',')[0].strip()
        # Inventory of the RaspberryShake stations
        inventory = raspberry.get_S_inventory()

        for sta in inventory[0]:
            x = sta.longitude
            y = sta.latitude 
            
            if sta.code == selected_sta_code:
                ax.plot(x, y, 'bv', markersize=15, transform=ccrs.Geodetic())

                # Check the region scale to decide if station names should be shown
                if raspberry.is_region_switzerland():
                    ax.text(x, y + 0.05, sta.code, transform=ccrs.Geodetic(), 
                            fontsize=10, verticalalignment='bottom', horizontalalignment='center')
            else:
                ax.plot(x, y, 'kv', markersize=12, transform=ccrs.Geodetic(), alpha=0.5)

                # Check the region scale to decide if station names should be shown
                if raspberry.is_region_switzerland():
                    ax.text(x, y + 0.05, sta.code, transform=ccrs.Geodetic(), 
                            fontsize=9, verticalalignment='bottom', horizontalalignment='center')
        
        # Title
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        ax.set_title(f"{time}, Depth: {round(depth, 1)} km")

        # Draw standard features
        ax.gridlines()
        ax.coastlines()
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
    
        plt.savefig("map.png", dpi=200, bbox_inches='tight')
        plt.show()
        
