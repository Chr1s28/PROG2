import os
import requests_cache
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
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
    
    def visualize_data(self, viz_type='scatter'):
        """
        Visualize accident locations on an interactive map using Plotly.
        
        :param viz_type: Type of visualization ('scatter' or 'heatmap')
        :type viz_type: str
        :return: Plotly figure object
        :rtype: plotly.graph_objects.Figure
        """
        if self.processed_data is None:
            self.remove_language_columns()
        
        viz_data = self.processed_data.copy()
        
        # CHLV95 to WGS84
        transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
        
        coordinates = [
            transformer.transform(row.AccidentLocation_CHLV95_E, row.AccidentLocation_CHLV95_N) 
            for _, row in viz_data.iterrows()
        ]
        
        viz_data['longitude'] = [coord[0] for coord in coordinates]
        viz_data['latitude'] = [coord[1] for coord in coordinates]
        
        # Create the figure
        fig = go.Figure()
        
        if viz_type.lower() == 'scatter':
            # Add scatter plot with discrete colors for each severity category
            for severity in viz_data['AccidentSeverityCategory'].unique():
                # Filter data for this severity
                category_data = viz_data[viz_data['AccidentSeverityCategory'] == severity]
                
                # Add a trace for this severity category
                fig.add_trace(go.Scattermap(
                    lat=category_data['latitude'],
                    lon=category_data['longitude'],
                    mode='markers',
                    marker=dict(size=4),
                    name=severity,
                    hoverinfo='text'
                ))
            
        elif viz_type.lower() == 'heatmap':
            # Add heatmap with array of ones for z values
            fig.add_trace(go.Densitymap(
                lat=viz_data['latitude'],
                lon=viz_data['longitude'],
                z=[1] * len(viz_data),  # Array of ones with same length as data
                radius=10,
                colorscale='Hot',
                hoverinfo='none'
            ))
        
        # Update layout
        fig.update_layout(
            mapmode="maplibre",
            maplibre=dict(
                style='open-street-map',
                center=dict(
                    lat=viz_data['latitude'].mean(),
                    lon=viz_data['longitude'].mean()
                ),
                zoom=13
            ),
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            title='Road Traffic Accidents in Zurich',
            height=800
        )
        
        fig.show()
        
        return fig


# Example usage
url = "https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte/download/RoadTrafficAccidentLocations.parquet"

downloader = DatasetDownloader(url)
raw_dataset = downloader.load_as_dataframe()

# Process the dataset
processor = AccidentDataProcessor(raw_dataset)
clean_dataset = processor.remove_language_columns()

# Visualize the data as scatter points
print("Generating scatter map...")
processor.visualize_data(viz_type='scatter')

# Visualize the data as a heatmap
print("Generating heatmap...")
processor.visualize_data(viz_type='heatmap')
