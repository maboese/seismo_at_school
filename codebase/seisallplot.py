# -*- coding: utf-8 -*-
""" 
Plots vertical component seismograms from all stations 
for the selected earthquake.
"""
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, clear_output
import obspy
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth
from codebase import config
from codebase.seisplot import get_waveforms

# Network codes to plot
networks_to_plot = ['S']

# Colors for the networks
network_colors = {'CH': 'tab:cyan', 'S': 'black'}

def plot_all_seismograms(raspberry):
    # Time windows and frequencies for the seismograms, depending the region scale
    if raspberry.is_region_switzerland():
        timewindow_start = config.regions["switzerland"]["filt-time-range"][0]
        timewindow_end = config.regions["switzerland"]["filt-time-range"][1]
        fmin, fmax = config.regions["switzerland"]["filt-freq-range"]
    elif raspberry.is_region_europe():
        timewindow_start = config.regions["europe"]["filt-time-range"][0]
        timewindow_end = config.regions["europe"]["filt-time-range"][1]
        fmin, fmax = config.regions["europe"]["filt-freq-range"]
    else:
        timewindow_start = config.regions["worldwide"]["filt-time-range"][0]
        timewindow_end = config.regions["worldwide"]["filt-time-range"][1]
        fmin, fmax = config.regions["worldwide"]["filt-freq-range"]
    
    # Use the seismogram plot output widget.
    with raspberry.seis_output:
        clear_output(wait=True)

        # Get the selected earthquake
        selected_eq  = raspberry.get_earthquake_quakeml()
        lon = selected_eq.origins[0].longitude
        lat = selected_eq.origins[0].latitude
        mag = selected_eq.magnitudes[0].mag
        depth = selected_eq.origins[0].depth / 1000.0
        origin_time = selected_eq.origins[0].time

        if depth < 0:
            depth = 0.0

        # Combine all the networks into one inventory
        inventory = obspy.Inventory()
        if 'S' in networks_to_plot:
            inventory += raspberry.get_S_inventory()
        if 'CH' in networks_to_plot:
            inventory += raspberry.get_CH_inventory()

        # Lists to store the distances, traces and labels
        distances = []
        traces = []
        labels = []
        dist_labels = []
        label_locs = []
        peak_amplitudes = []

        # Loop over the networks
        for net_idx, network in enumerate(networks_to_plot):
            stations = inventory[net_idx]
            # total number of stations
            total_steps = len(stations)
            
            for sta_idx, station in enumerate(stations):
                sta_lat = station.latitude
                sta_lon = station.longitude
                station_name = station.code
                
                # Get the seismogram. Use a try-except block to catch any errors and pass them.
                try:
                    st = get_waveforms(origin_time, timewindow_start, timewindow_end, station_name)

                    # Calculate the progress percentage
                    progress = (sta_idx + 1) / total_steps * 100
                    # Print the progress percentage on the same line
                    print(f"{network}.{station_name} --- Progress: {progress:.2f}%", end='\r')
                    
                    if st and len(st) > 0:
                        # Calculate the distance
                        distance, _, _ = gps2dist_azimuth(lat, lon, sta_lat, sta_lon)
                        distance = distance / 1000.0
                        
                        # Filter the seismogram
                        st.merge(fill_value='interpolate', method=0)
                        st.detrend("demean")
                        tr = st.select(component="Z")[0]
                        tr.remove_response(output="VEL")
                        tr.filter("bandpass", freqmin=fmin, freqmax=fmax, corners=4, zerophase=True)
                        tr.trim(starttime=origin_time, endtime=origin_time + timewindow_end)

                        # Add the trace to the list
                        traces.append(tr)
                        distances.append(distance)
                        peak_amplitudes.append(max(abs(tr.data)))
                        dist_labels.append(round(distance, 1))
                        labels.append(f"{network}.{station_name}")
                        label_locs.append(distance)
                except Exception as e:
                    pass

        print("")
        print(f"Number of seismograms: {len(traces)}")

        if len(traces) == 0:
            print("No seismograms found for the selected earthquake.")
            return
        
        # Plot the seismograms at their respective distances. The amplitudes
        # are normalized to the maximum amplitude of each trace similar to
        # obspy section plot. It is also possible to plot the seismograms with
        # relative amplitudes normalized with the maximum of the peak amplitudes.
        fig, ax = plt.subplots(figsize=(10, 12))

        for idx, trace in enumerate(traces):
            net = trace.stats.network

            # Plot with individually scaled amplitudes
            ax.plot(tr.times(), 5 * trace.data / max(abs(trace.data)) + distances[idx],
                    color=network_colors[net], label=labels[idx], linewidth=0.25,
                    alpha=0.5)

            # # Plot with relative amplitudes with respect to the maximum peak amplitude
            # ax.plot(tr.times(), 50 * trace.data / max(peak_amplitudes) + distances[idx],  
            #         color=network_colors[net], label=labels[idx], linewidth=0.5, 
            #         alpha=0.8)
            
            
            # Plot the station names right-hand side of the seismograms outside the plot area
            ax.text(timewindow_end + 1, distances[idx], labels[idx], 
                    fontsize=8,  verticalalignment='center', 
                    horizontalalignment='left', color=network_colors[net], 
                    clip_on=False)
            
        model = TauPyModel(model='iasp91')
        p = []
        s = []
        p_dist = []
        s_dist = []
        for d in distances + [max(distances) + 50]:
            # P-wave arrival
            arrivals = model.get_ray_paths(
                source_depth_in_km=depth, 
                distance_in_degree=d/111., 
                phase_list=config.p_phases)
            
            p.append(arrivals[0].time)
            p_dist.append(d)

            # S-wave arrival
            arrivals = model.get_ray_paths(
                source_depth_in_km=depth, 
                distance_in_degree=d/111., 
                phase_list=config.s_phases)
            
            s.append(arrivals[0].time)
            s_dist.append(d)

        # Sort the distances and travel times tigether
        p, p_dist = zip(*sorted(zip(p, p_dist)))
        s, s_dist = zip(*sorted(zip(s, s_dist)))

        ax.plot(p, p_dist, color='red', label='P', linewidth=2.0, linestyle=':')
        ax.plot(s, s_dist, color='blue', label='S', linewidth=2.0, linestyle=':') 

        ax.set_title(f"{origin_time} (M{mag:.1f}, Z= {depth:.1f} km)")
        ax.set_xlabel("Time/Zeit [s]")
        ax.set_ylabel("Distance/Entfernung [km]")
        ax.grid(axis='x', linestyle=':', linewidth=0.5)
        ax.set_xlim(0, timewindow_end)

        # Set the y-axis limits if the region scale is Switzerland
        if raspberry.is_region_switzerland():
            ax.set_ylim(0, max(distances) + 50)

        if len(traces) > 0:
            plt.savefig('waveform_section.png', dpi=200, bbox_inches='tight')
            plt.show()


        # Distance vs. amplitude plot. Use it a try-except block to catch any errors 
        # and to avoid empty figures shown in the notebook.
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(dist_labels, np.asarray(peak_amplitudes) * 100, color='tab:cyan',
                       edgecolors='black', s=40)
            ax.set_xlabel("Distance [km]")
            ax.set_ylabel("Peak amplitude [cm/s]")
            ax.set_title("Distance vs. peak amplitude")
            ax.grid(axis='both', linestyle=':', linewidth=0.5, which='both')
            ax.set_yscale('log')
            ax.set_xscale('log')
            plt.savefig('distance_vs_amplitude.png', dpi=200, bbox_inches='tight')
            plt.show()
        except Exception as e:
            print("Error plotting distance vs. amplitude:", e)
            pass
              

