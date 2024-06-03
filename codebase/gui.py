# -*- coding: utf-8 -*-
from ipywidgets import widgets, interact, Dropdown, Select
import numpy as np
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from codebase import config

# Years that will be used in the dropdown. It cannot excced the current year
start_year = 2023

_labels = {
    'en': {
        'year': 'Year', 
        'region': 'Region',
        'region_values': ['Worldwide', 'Europe', 'Switzerland'],
        'earthquake': 'Earthquakes',
        'raspberry': 'Raspberry'},
           
    'de': {
        'year': 'Jahr', 
        'region': 'Bereich',
        'region_values': ['Weltweit', 'Europa', 'Schweiz'],
        'earthquake': 'Erdbeben',
        'raspberry': 'Raspberry'}
}


def correct_region_key(key):
    """ 
    Function to convert the region name to English to be used as a key. 
    For example, 'Schweiz' will be converted to 'switzerland' 
    """
    if key.lower() == 'schweiz':
        key = 'switzerland'
    elif key.lower() == 'europa':
        key = 'europe'
    elif key.lower() == 'weltweit':
        key = 'worldwide'
    return key.lower()

class RaspberryShake:
    def __init__(self):
        self.stations = config.rs_sta_list
    
    def query_web_services(self):
        """ Function to query the server with the selected parameters """
        server = self.get_parameters()['server']
        min_mag = self.get_selected_min_mag()
        max_mag = 10.0
        
        year = self.get_selected_year()
        start = UTCDateTime(f"{year}-01-01T00:00:00")
        end = UTCDateTime(f"{year}-12-31T23:59:59")
        
        # FDSN client
        client = Client(server)
        
        # Query depending on the region
        region = self.get_selected_region()
        if region.lower() in ['europa', 'europe']:
            # For Europe, server will be IRIS. Downscale the region
            # by adjusting the latitude and longitude
            min_lat = 38.0
            max_lat = 70.0
            min_lon = -15.0
            max_lon = 30.0
            
            return client.get_events(starttime=start, 
                                     endtime=end,
                                     minmagnitude=min_mag,
                                     maxmagnitude=max_mag,
                                     minlatitude=min_lat,
                                     maxlatitude=max_lat,
                                     minlongitude=min_lon,
                                     maxlongitude=max_lon)
        else:
            # The server is ETH for Switzerland, and IRIS for worldwide
            # No need to downscale the region for either case.
            return client.get_events(starttime=start, 
                                     endtime=end,
                                     minmagnitude=min_mag,
                                     maxmagnitude=max_mag)

    def get_magnitudes_for_region(self, region):
        """ Return a set of magnitude values for the given region """
        region = correct_region_key(region)
        return config.regions[region.lower()]['magnitudes']

    def handle_year_changed(self, selection):
        """ Event to evaluate the year and reset the earthquake list """
        # Get the new year selection
        year = selection['new']
        
        # Disable the earthquake dropdown until the list is updated
        self.earthquake_combo.options = ["Loading..."]

        # Query the web services
        events = self.query_web_services()
        
        # Get the list of earthquakes
        eq_list = [f"Magnitude {np.around(event.magnitudes[0].mag, decimals=1)}    {event.origins[0].time}    {event.event_descriptions[0].text}" for event in events]
        
        # Update the earthquake dropdown
        self.earthquake_combo.options = eq_list

        # Display the first earthquake in the list
        if len(eq_list) > 0:
            self.earthquake_combo.value = eq_list[0]

        # Enable the earthquake dropdown
        self.earthquake_combo.disabled = False

    def handle_region_changed(self, selection):
        """ Event to evaluate the region and reset magnitudes """
        # Get the new region selection
        region  = correct_region_key(selection['new'])

        # Reset the magnitude select widget
        self.magnitude_select.options = self.get_magnitudes_for_region(region)

    def handle_magnitude_changed(self, selection):
        """ Event to evaluate the magnitude and reset the earthquake list """
        def _earthquake_info(event):
            """ Return the earthquake information """
            return f"Magnitude {np.around(event.magnitudes[0].mag, decimals=1)}    {event.origins[0].time}    {event.event_descriptions[0].text}" 
        # Get the new magnitude selection
        magnitude = selection['new']
        
        # Get the parameters
        parameters = self.get_parameters()
        parameters['min_mag'] = magnitude
        
        # Disable the earthquake dropdown until the list is updated
        self.earthquake_combo.options = ["Loading..."]

        # Query the web services
        events = self.query_web_services()
        
        # Get the list of earthquakes
        eq_list = [_earthquake_info(event) for event in events]
        
        # Update the earthquake dropdown
        self.earthquake_combo.options = eq_list

        # Display the first earthquake in the list
        if len(eq_list) > 0:
            self.earthquake_combo.value = eq_list[0]

        # Enable the earthquake dropdown
        self.earthquake_combo.disabled = False

    def get_selected_station(self):
        """ Return the selected station """
        return self.raspberry_combo.value
    
    def get_selected_earthquake(self):
        """ Return the selected earthquake """
        return self.earthquake_combo.value
    
    def get_selected_year(self):
        """ Return the selected year """
        return self.year_combo.value
    
    def get_selected_region(self):
        """ Return the selected region """
        return self.region_select.value
    
    def get_selected_min_mag(self):
        """ Return the selected minimum magnitude """
        return self.magnitude_select.value
    
    def get_parameters(self):
        """ Return the query and processing parameters """
        freq_min, freq_max = config.regions[correct_region_key(self.region_select.value)]['filt-freq-range']
        time_min, time_max = config.regions[correct_region_key(self.region_select.value)]['filt-time-range']

        if self.get_selected_region().lower() in ['switzerland', 'schweiz']:
            server = 'ETH'
        else:
            server = 'IRIS'
        
        return {
            'server': server,
            'station': self.get_selected_station(),
            'year': self.get_selected_year(),
            'region': self.get_selected_region(),
            'earthquake': self.get_selected_earthquake(),
            'freq_min': freq_min,
            'freq_max': freq_max,
            'time_min': time_min,
            'time_max': time_max
        }
    
    def setup_gui(self, language="en"):
        """ Function to setup the GUI for the application"""
        # Labels for the GUI, depending on the language
        language = language.lower()
        if language not in _labels.keys():
            raise ValueError(f"Language {language} is not supported. Use 'en' or 'de'.")

        # Widget labels depending on the language
        _year_label = _labels[language]['year']
        _region_label = _labels[language]['region']
        _station_label = _labels[language]['raspberry']
        _eq_label = _labels[language]['earthquake']

        # Dropdown for year
        years = [str(i) for i in range(start_year, UTCDateTime().year + 1)]
        self.year_combo = Dropdown(options=[str(i) for i in years], description=_year_label)

        # List box for region
        _region_options = _labels[language]['region_values']
        self.region_select = Select(options=_region_options, description=_region_label)
        
        # Minimum magnitude allowed for each region scale
        self.magnitude_select = Select(
            options=self.get_magnitudes_for_region(self.region_select.value), 
            description='Min.\nMagnitude')
        
        # Dropdown for the Raspberry Shake station list
        self.raspberry_combo = Dropdown(options=[station[3] for station in self.stations], 
                                         description=_station_label)
        
        # Dropdown for earthquakes
        self.earthquake_combo = Dropdown(options=[], description=_eq_label)

        # Initial fill of the earthquake list
        self.handle_magnitude_changed({'new': self.magnitude_select.value})

        # Connect the signals
        self.year_combo.observe(self.handle_year_changed, names='value')
        self.region_select.observe(self.handle_region_changed, names='value')
        self.magnitude_select.observe(self.handle_magnitude_changed, names='value')

    def display(self):
        """ Display the widgets """
        query_components = widgets.VBox([self.year_combo, 
                                         self.region_select, 
                                         self.magnitude_select,
                                         self.raspberry_combo])
        events = widgets.VBox([self.earthquake_combo], style={'overflow-y': 'scroll'})
        
        # Make the events VBox span the entire height
        events.layout.height = '200%'
        gui_components = widgets.HBox([query_components, events])
        display(gui_components)

    
