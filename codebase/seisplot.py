# -*- coding: utf-8 -*-
""" 
Plots the 3-component seismogram of the selected earthquake as
recorded at the selected station.
"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from IPython.display import display, clear_output
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth
from codebase import config

def predict_arrivals(station_lon, station_lat, event_lon, event_lat, event_depth_in_km, phase_list):
    """
    Predicts the phase arrivals for the given earthquake and station parameters.
    """
    if not isinstance(phase_list, list):
        phase_list = [phase_list]

    model = TauPyModel(model="iasp91")
    distance, _, _ = gps2dist_azimuth(station_lat, station_lon, 
                                      event_lat, event_lon)
    distance = distance / 1000.0
    arrivals = model.get_travel_times(source_depth_in_km=event_depth_in_km,
                                      distance_in_degree=distance/111.0,
                                      phase_list=phase_list)
    return arrivals


def get_waveforms(origin_time, timewindow_start, timewindow_end, sta_code):
    """ Download the waveform data for the selected station and earthquake"""
    try:
        stream = Client("ETH").get_waveforms(
            network="S", station=sta_code, location="*", channel="EH*", 
            starttime=origin_time + timewindow_start - 60,
            endtime=origin_time + timewindow_end + 60, attach_response=True)
    except:
        try:
            stream = Client("ETH").get_waveforms(
                network="CH", station=sta_code, location="*", channel="HH*",
                starttime = origin_time + timewindow_start - 60, 
                endtime = origin_time + timewindow_end + 60, attach_response=True)
        except Exception as e:
            stream = None

    return stream

def plot_three_component_seismogram(stream, axZ, axN, axE):
    """
    Plots the 3-component seismogram for the given stream on the given axes.
    """
    for tr in stream:
        if tr.stats.channel[-1] == 'Z':
            axZ.plot(tr.times("matplotlib"), tr.data, label=tr.stats.channel,
                    color='black', lw=1, alpha=0.7)
            axZ.xaxis_date()
            
        elif tr.stats.channel[-1] == 'N':
            axN.plot(tr.times("matplotlib"), tr.data, label=tr.stats.channel,
                    color='black', lw=1, alpha=0.7)
            axN.xaxis_date()
            
        else:
            axE.plot(tr.times("matplotlib"), tr.data, label=tr.stats.channel,
                    color='black', lw=1, alpha=0.7)
            axE.xaxis_date()
            axE.set_ylabel('Velocity [m/s]')
            axE.set_xlabel('Time [UTC]')

    for ax in [axZ, axN, axE]:
        ax.legend(loc='upper right')
        
def plot_phase(axes, phase_time, color, phase_name):
    """ Plots the predicted phase arrival time on the given axes. """
    for ax in axes:
        ax.axvline(phase_time, color=color, linestyle='--', lw=2,
                   label=f"{phase_name}")
        
def seismogram_plot(raspberry):
    """ Plots the waveform of the selected earthquake at the selected station """
    # Get the selected earthquake and station as quakeml and inventory objects
    selected_eq  = raspberry.get_earthquake_quakeml()
    selected_sta = raspberry.get_selected_station_inventory()[0][0]

    # Event parameters
    event_lon = selected_eq.origins[0].longitude
    event_lat = selected_eq.origins[0].latitude
    mag = selected_eq.magnitudes[0].mag
    origin_time = selected_eq.origins[0].time
    region = selected_eq.event_descriptions[0].text
    depth_in_km = selected_eq.origins[0].depth / 1000.0
    if depth_in_km < 0:
        print(f"The depth is negative at {depth_in_km}, setting it to 0 km")
        depth_in_km = 0.0

    # Station parameters
    station_lon = selected_sta.longitude
    station_lat = selected_sta.latitude
    station_name = selected_sta.code
    sed_station_name = raspberry.get_sed_station()

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

    # Use the output widget to display the seismogram
    with raspberry.seis_output:
        clear_output()
        
        print(f"Selected earthquake:")
        print(f"  Location: {event_lon:.2f} E, {event_lat:.2f} N")
        print(f"  Magnitude: {mag:.1f}")
        print(f"  Depth: {depth_in_km:.1f} km")
        print(f"  Origin time: {origin_time}")
        print(f"  Region: {region}")
        print("\n")

        # Get the waveforms for raspberry shake and the closest SED station
        stream = get_waveforms(origin_time, timewindow_start, timewindow_end, station_name)
        sed_stream = get_waveforms(origin_time, timewindow_start, timewindow_end, sed_station_name)

        # RasberryShake waveforms
        if stream:
            fig, (axZ, axN, axE) = plt.subplots(nrows=3, ncols=1, figsize=(11, 4),
                                            sharex=True, sharey=True)
            axZ.set_title(f"Raspberry Shake {station_name}", fontsize=12)

            # Pre-process before plotting
            stream.merge(fill_value='interpolate', method=0)
            stream.detrend('demean')
            stream.filter('bandpass', freqmin=fmin, freqmax=fmax, corners=4, zerophase=True)
            stream.remove_response(output="VEL")
            stream.trim(starttime=origin_time + timewindow_start, 
                        endtime=origin_time + timewindow_end)
            
            # Plot the seismogram on the axes
            plot_three_component_seismogram(stream, axZ, axN, axE)
            
            distance = gps2dist_azimuth(station_lat, station_lon, event_lat, event_lon)[0]
            print(f"Distance between the event and the station {station_name}: {distance/1000:.1f} km")

            # Predict the P and S arrivals. The first arriving P/S will be 
            # determined from the list returned by the TauPyModel
            P_arrival = predict_arrivals(
                station_lon, station_lat, event_lon, event_lat, depth_in_km, config.p_phases)
            S_arrival = predict_arrivals(
                station_lon, station_lat, event_lon, event_lat, depth_in_km, config.s_phases)
                
            P_arrival.sort(key=lambda x: x.time)
            S_arrival.sort(key=lambda x: x.time)

            if P_arrival is not None and len(P_arrival) > 0:
                print(f"{P_arrival[0].name} arrival at {station_name}: {round(P_arrival[0].time, 2)} s")
                plot_phase(axes=[axZ, axN, axE], phase_time=origin_time + P_arrival[0].time,
                           color='tab:red', phase_name='P')
            else:
                print(f"P arrival at {station_name}: No prediction available")

            if S_arrival is not None and len(S_arrival) > 0:
                print(f"{S_arrival[0].name} arrival at {station_name}: {round(S_arrival[0].time, 2)} s")
                plot_phase(axes=[axZ, axN, axE], phase_time=origin_time + S_arrival[0].time,
                           color='tab:blue', phase_name='S')
            else:
                print(f"S arrival at {station_name}: No prediction available")

            
            # Set the x-limit to the time window
            axZ.set_xlim(origin_time + timewindow_start, origin_time + timewindow_end)

            plt.savefig("S.{station_name}_seismogram.png", dpi=200, bbox_inches='tight')
            plt.show()
            
        else:
            print(f"No data available for station {station_name} at Raspberry Shake network")

        # SED waveforms
        if sed_stream:
            fig, (axZ, axN, axE) = plt.subplots(nrows=3, ncols=1, figsize=(11, 4),
                                            sharex=True, sharey=True)
            axZ.set_title(f"SED {sed_station_name}", fontsize=12)
            # Pre-process before plotting
            sed_stream.merge(fill_value='interpolate', method=0)
            sed_stream.detrend('demean')
            sed_stream.filter('bandpass', freqmin=fmin, freqmax=fmax, corners=4, zerophase=True)
            sed_stream.remove_response(output="VEL")
            sed_stream.trim(starttime=origin_time + timewindow_start, 
                            endtime=origin_time + timewindow_end)
            
            plot_three_component_seismogram(sed_stream, axZ, axN, axE)

            # SED station info
            sed_sta = raspberry.get_sed_station_inventory()[0][0]
            sed_lat = sed_sta.latitude
            sed_lon = sed_sta.longitude
            distance = gps2dist_azimuth(sed_lat, sed_lon, event_lat, event_lon)[0]
            print(f"Distance between the event and the station {sed_station_name}: {distance/1000:.1f} km")

            # Predict the P and S arrivals
            p_phases = ['p', 'Pg', 'Pn' , 'PmP', 'P', 'PP', 'Pdiff']
            s_phases = ['s', 'Sg', 'Sn' , 'SmS', 'S', 'SS', 'Sdiff']

            P_arrival = predict_arrivals(
                sed_lon, sed_lat, event_lon, event_lat, depth_in_km, config.p_phases)
            S_arrival = predict_arrivals(
                sed_lon, sed_lat, event_lon, event_lat, depth_in_km, config.s_phases)
            
            P_arrival.sort(key=lambda x: x.time)
            S_arrival.sort(key=lambda x: x.time)
            
            if P_arrival is not None and len(P_arrival) > 0:
                print(f"{P_arrival[0].name} arrival at {station_name}: {round(P_arrival[0].time, 2)} s")
                plot_phase(axes=[axZ, axN, axE], phase_time=origin_time + P_arrival[0].time, 
                           color='tab:red', phase_name=P_arrival[0].name)
            
            else:
                print(f"P arrival at {sed_station_name}: No prediction available")

            if S_arrival is not None and len(S_arrival) > 0:
                print(f"{S_arrival[0].name} arrival at {station_name}: {round(S_arrival[0].time, 2)} s")
                plot_phase(axes=[axZ, axN, axE], phase_time=origin_time + S_arrival[0].time, 
                           color="tab:blue", phase_name=S_arrival[0].name)
            else:
                print(f"S arrival at {sed_station_name}: No prediction available")

            # Set the x-limit to the time window
            axZ.set_xlim(origin_time + timewindow_start, origin_time + timewindow_end)

            plt.savefig("CH.{station_name}_seismogram.png", dpi=200, bbox_inches='tight')
            plt.show()

        else:
            print(f"No data available for station {sed_station_name} at Swiss network")
                    
        
