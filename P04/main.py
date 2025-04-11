import os
import requests_cache
import pandas as pd
import re
import plotly.express as px
from pyproj import Transformer
from datetime import timedelta

class DatasetDownloader:
    """
    A class to download datasets with caching functionality to prevent
    multiple downloads within a specified time period.
    """
    
    def __init__(self, url, cache_seconds=10):
        """
        Initialize the DatasetDownloader with a URL and cache period.
        
        :param url: The URL of the dataset to download
        :type url: str
        :param cache_seconds: Seconds to keep responses in cache
        :type cache_seconds: int
        """
        self.url = url
        self.local_filename = os.path.basename(url)
        
        # Initialize the cached session
        self.session = requests_cache.CachedSession(
            'dataset_cache',  # Cache name/file
            expire_after=timedelta(seconds=cache_seconds),
            allowable_methods=('GET', 'POST')
        )
    
    def download(self, force=False):
        """
        Download the dataset using cache if available.
        
        :param force: Force download even if cached version exists
        :type force: bool
        :return: Path to the downloaded file
        :rtype: str
        """
        if force:
            # Clear the cache for this URL if forcing download
            self.session.cache.delete_url(self.url)
            
        print(f"Requesting dataset from {self.url}")
        response = self.session.get(self.url, stream=True)
        response.raise_for_status()
        
        if getattr(response, 'from_cache', False) and not force:
            print("Using cached response (no download needed)")
        else:
            print("Downloading fresh data")
            with open(self.local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Download completed: {self.local_filename}")
            
        return self.local_filename
    
    def load_as_dataframe(self, force_download=False):
        """
        Download the dataset and load it as a pandas DataFrame.
        
        :param force_download: Force download even if cached version exists
        :type force_download: bool
        :return: DataFrame containing the dataset
        :rtype: pandas.DataFrame
        """
        filename = self.download(force=force_download)
        return pd.read_parquet(filename)

class AccidentDataProcessor:
    """
    A class to preprocess and visualize the road traffic accident dataset.
    """
    
    def __init__(self, dataframe):
        """
        Initialize the processor with a pandas DataFrame.
        
        :param dataframe: The accident dataset
        :type dataframe: pandas.DataFrame
        """
        self.raw_data = dataframe
        self.processed_data = None
    
    def remove_language_columns(self):
        """
        Remove columns with language-specific suffixes (_de, _fr, _it).
        Keep only the base columns and English (_en) translations.
        
        :return: DataFrame with language columns removed
        :rtype: pandas.DataFrame
        """
        # Get all column names
        all_columns = self.raw_data.columns.tolist()
        
        # Identify columns to keep (no language suffix or _en suffix)
        columns_to_keep = []
        for col in all_columns:
            # Keep if it doesn't end with _de, _fr, or _it
            if not re.search(r'_(de|fr|it)$', col):
                columns_to_keep.append(col)
        
        # Create a new DataFrame with only the selected columns
        self.processed_data = self.raw_data[columns_to_keep].copy()
        return self.processed_data
    
    def get_processed_data(self):
        """
        Get the processed DataFrame. If processing hasn't been done yet,
        perform the default processing steps first.
        
        :return: Processed DataFrame
        :rtype: pandas.DataFrame
        """
        if self.processed_data is None:
            self.remove_language_columns()
        return self.processed_data
    
    def visualize_data(self, map_type='open-street-map', zoom=11):
        """
        Visualize accident locations on an interactive map using Plotly.
        
        :param map_type: Type of map to display ('open-street-map', 'carto-positron', etc.)
        :type map_type: str
        :param zoom: Initial zoom level for the map
        :type zoom: int
        :return: Plotly figure object
        :rtype: plotly.graph_objects.Figure
        """
        # Make sure we have processed data
        if self.processed_data is None:
            self.remove_language_columns()
        
        # Create a copy of the data for visualization
        viz_data = self.processed_data.copy()
        
        # Convert Swiss coordinates (CHLV95) to WGS84 (latitude/longitude)
        transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
        
        # Apply the transformation to each row
        coordinates = [
            transformer.transform(row.AccidentLocation_CHLV95_E, row.AccidentLocation_CHLV95_N) 
            for _, row in viz_data.iterrows()
        ]
        
        # Add latitude and longitude columns
        viz_data['longitude'] = [coord[0] for coord in coordinates]
        viz_data['latitude'] = [coord[1] for coord in coordinates]
        
        # Create hover text with accident details
        viz_data['hover_text'] = viz_data.apply(
            lambda row: f"<b>Accident Type:</b> {row.get('AccidentType_en', 'N/A')}<br>" +
                       f"<b>Severity:</b> {row.get('AccidentSeverityCategory_en', 'N/A')}<br>" +
                       f"<b>Date:</b> {row.get('AccidentMonth_en', 'N/A')} {row.get('AccidentYear', 'N/A')}<br>" +
                       f"<b>Time:</b> {row.get('AccidentHour_text', 'N/A')}<br>" +
                       f"<b>Road Type:</b> {row.get('RoadType_en', 'N/A')}<br>" +
                       f"<b>Canton:</b> {row.get('CantonCode', 'N/A')}",
            axis=1
        )
        
        # Create color mapping based on accident severity
        color_column = 'AccidentSeverityCategory'
        
        # Create the map
        fig = px.scatter_mapbox(
            viz_data,
            lat='latitude',
            lon='longitude',
            hover_name='AccidentUID',
            hover_data={
                'latitude': False,
                'longitude': False,
                'AccidentUID': False,
                'hover_text': True
            },
            color=color_column,
            zoom=zoom,
            height=800,
            title='Road Traffic Accidents in Zurich'
        )
        
        # Update hover template to use the custom hover_text
        fig.update_traces(
            hovertemplate="%{customdata[0]}",
            marker=dict(size=8)
        )
        
        # Update the map layout
        fig.update_layout(
            mapbox_style=map_type,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            legend_title_text='Accident Severity'
        )
        
        # Show the figure
        fig.show()
        
        return fig


# Example usage
url = "https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte/download/RoadTrafficAccidentLocations.parquet"

downloader = DatasetDownloader(url)
raw_dataset = downloader.load_as_dataframe()

# Process the dataset
processor = AccidentDataProcessor(raw_dataset)
clean_dataset = processor.remove_language_columns()

# Display information about the processed dataset
print(f"Original dataset shape: {raw_dataset.shape}")
print(f"Processed dataset shape: {clean_dataset.shape}")
print("\nColumns in processed dataset:")
for col in clean_dataset.columns[:10]:  # Show just the first 10 columns
    print(f"- {col}")

# Visualize the data on a map
processor.visualize_data(zoom=12)
