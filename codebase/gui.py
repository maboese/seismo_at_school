# -*- coding: utf-8 -*-
from ipywidgets import widgets, interact, Dropdown, Select
from IPython.display import display
import importlib
import numpy as np
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from codebase import config

# Years that will be used in the dropdown. It cannot excced the current year
start_year = 2023

# Labels for the widgets
_labels = {
    'en': {
        'year': 'Year', 
        'region': 'Region',
        'region_values': ['Worldwide', 'Europe', 'Switzerland'],
        'earthquake': 'Earthquakes',
        'raspberry': 'Raspberry',
        'plotmap': 'Plot event',
        'plotseis': 'Plot Seismograms'},
           
    'de': {
        'year': 'Jahr', 
        'region': 'Bereich',
        'region_values': ['Weltweit', 'Europa', 'Schweiz'],
        'earthquake': 'Erdbeben',
        'raspberry': 'Raspberry',
        'plotmap': 'Erdbeben plotten',
        'plotseis': 'Seismogramme plotten'}
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
        self.catalog = []
        self.inventory = None

    def query_stations(self):
        # SED broadband stations:
        inv_ch = Client("ETH").get_stations(
            network="CH", station="*", location="--", channel="HH*", level="RESP")
        inv_ch = inv_ch.select(
            channel="*Z", station="*", time=UTCDateTime("2050-01-01T01:00:00.000Z"))

        # Seismo-at-school RaspberryShake stations
        inv_s = Client("ETH").get_stations(
            network="S", station="*",location="--", channel="EH*", level="RESP")
        inv_s = inv_s.select(
            channel="*Z", station="*", time=UTCDateTime("2050-01-01T01:00:00.000Z"))

        # Combine the inventories
        self.inventory = inv_ch + inv_s

    def get_CH_inventory(self):
        """ Return the inventory for Swiss network"""
        if self.inventory is None:
            self.query_stations()
        return self.inventory.select(network="CH")
    
    def get_S_inventory(self):
        """ Return the inventory for seismo-at-school network"""
        if self.inventory is None:
            self.query_stations()
        return self.inventory.select(network="S")
    
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
            
            try:
                self.catalog = client.get_events(
                    starttime=start, endtime=end, minmagnitude=min_mag,
                    maxmagnitude=max_mag, minlatitude=min_lat, maxlatitude=max_lat, 
                    minlongitude=min_lon, maxlongitude=max_lon)
            except:
                self.catalog = []

            return self.catalog
        else:
            # The server is ETH for Switzerland, and IRIS for worldwide
            # No need to downscale the region for either case.
            try:
                self.catalog = client.get_events(
                    starttime=start, endtime=end, minmagnitude=min_mag, 
                    maxmagnitude=max_mag)
            except:
                self.catalog = []
                
            return self.catalog

    def is_region_switzerland(self):
        """ Return True if the selected region is Switzerland """
        return self.get_selected_region().lower() == 'schweiz' or \
            self.get_selected_region().lower() == 'switzerland'
    
    def is_region_europe(self):
        """ Return True if the selected region is Europe """
        return self.get_selected_region().lower() == 'europa' or \
            self.get_selected_region().lower() == 'europe'
    
    def is_region_worldwide(self):
        """ Return True if the selected region is Worldwide """
        return self.get_selected_region().lower() == 'weltweit' or \
            self.get_selected_region().lower() == 'worldwide'
    
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
    
    def get_sed_station(self):
        """ Return the inventory of the selected station """
        rs_code = self.get_selected_station().split(',')[0].strip()

        # Find the station in the dictionary
        for station in self.stations:
            if station[0] == rs_code:
                return station[2]
        return None
    
    def get_sed_station_inventory(self):
        """ Return the inventory of the selected station """
        if self.inventory is None:
            self.query_stations()
        sta_code = self.get_sed_station()
        return self.inventory.select(station=sta_code)
    
    def get_selected_earthquake(self):
        """ Return the selected earthquake """
        return self.earthquake_combo.value
    
    def get_selected_station_inventory(self):
        """ Return the inventory of the selected station """
        if self.inventory is None:
            self.query_stations()
        sta_code = self.get_selected_station().split(',')[0].strip()
        return self.inventory.select(station=sta_code)
    
    def get_earthquake_quakeml(self):
        idx = self.earthquake_combo.options.index(self.earthquake_combo.value)
        return self.catalog[idx]
    
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
        self.earthquake_combo = Dropdown(options=[])
        # Use a separate label for the earthquake dropdown
        self.eq_label = widgets.Label(value=_eq_label)

        # Initial fill of the earthquake list
        self.handle_magnitude_changed({'new': self.magnitude_select.value})

        # Query the inventory
        self.query_stations()

        # Button to plot the location map of the selected earthquake
        self.plot_map_button = widgets.Button(description=_labels[language]['plotmap'],
                                              button_style='danger')
        self.plot_map_button.on_click(self.plot_map)

        # Button to plot the seismograms
        self.plot_seis_button = widgets.Button(description=_labels[language]['plotseis'],
                                                button_style='danger')
        self.plot_seis_button.on_click(self.plot_seismograms)

        # Button to plot all the seismograms 
        self.plot_all_seis_button = widgets.Button(description='Plot all seismograms',
                                                    button_style='danger')
        self.plot_all_seis_button.on_click(self.plot_all_seismograms)

        # Connect the signals
        self.year_combo.observe(self.handle_year_changed, names='value')
        self.region_select.observe(self.handle_region_changed, names='value')
        self.magnitude_select.observe(self.handle_magnitude_changed, names='value')
        
        # Create an output widget
        self.plot_output = widgets.Output()

        # Output widget for the seismograms
        self.seis_output = widgets.Output()

    def plot_map(self, event=None):
        """ Plot the location map """
        from codebase import mapplot, seisplot
        importlib.reload(mapplot)
        importlib.reload(seisplot)

        mapplot.plot_map(self)
        seisplot.seismogram_plot(self)
        
    def plot_all_seismograms(self, event=None):
        """ Plot all the seismograms """
        from codebase import seisallplot
        importlib.reload(seisallplot)
        seisallplot.plot_all_seismograms(self)

    def plot_seismograms(self, event=None):
        """ Plot the seismograms (not the map) """
        from codebase import seisplot
        importlib.reload(seisplot)
        seisplot.seismogram_plot(self)

    def display_map(self):
        """ Displays only the map """
        display(widgets.HBox([self.plot_output], layout=widgets.Layout(width='100%')))
        
    def display_seismograms(self):
        """ Displays only the seismograms """
        display(widgets.HBox([self.seis_output], layout=widgets.Layout(width='100%')))

    def display(self):
        """ Display the widgets """
        query_components = widgets.VBox([
            self.year_combo, 
            self.region_select, 
            self.magnitude_select,
            self.raspberry_combo
        ], layout=widgets.Layout(grid_area='query'))

        events = widgets.VBox([
            self.eq_label, 
            self.earthquake_combo,
            self.plot_map_button,
            # self.plot_seis_button
            self.plot_all_seis_button,
        ], layout=widgets.Layout(grid_area='events'))
        
        # Use a GridBox to create a 2x2 layout
        layout = widgets.GridBox([
            query_components,
            events,
        ], layout=widgets.Layout(
            width='100%',
            grid_template_columns='50% 50%',
            grid_template_rows='auto auto',
            grid_template_areas='''
            "query events"
            '''
        ))
        display(layout)

        # Display the output widget. Span the entire width
        # For this add another cell just below the layout
        # display(widgets.HBox([self.plot_output], layout=widgets.Layout(width='100%')))



