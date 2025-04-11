import os
import requests_cache
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pyproj import Transformer
from datetime import timedelta
from collections import Counter

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
    
    def calculate_statistics(self):
        """
        Calculate and print various statistics about the accident dataset.
        
        This includes:
        - Basic counts and distributions
        - Temporal patterns (yearly, monthly, daily, hourly)
        - Accident types and severity
        - Vehicle involvement statistics
        
        :return: Dictionary containing the calculated statistics
        :rtype: dict
        """
        if self.processed_data is None:
            self.remove_language_columns()
        
        data = self.processed_data
        stats = {}
        
        # Basic dataset statistics
        stats['total_accidents'] = len(data)
        print(f"\n===== ACCIDENT DATASET STATISTICS =====")
        print(f"Total number of accidents: {stats['total_accidents']}")
        
        # Accident severity distribution
        severity_counts = data['AccidentSeverityCategory'].value_counts()
        severity_percentages = (severity_counts / stats['total_accidents'] * 100).round(1)
        stats['severity_distribution'] = severity_counts.to_dict()
        
        print("\n----- Accident Severity Distribution -----")
        for severity, count in severity_counts.items():
            severity_name = data[data['AccidentSeverityCategory'] == severity]['AccidentSeverityCategory_en'].iloc[0]
            print(f"{severity} ({severity_name}): {count} accidents ({severity_percentages[severity]}%)")
        
        # Vehicle involvement
        vehicle_stats = {
            'Pedestrian': data['AccidentInvolvingPedestrian'].value_counts().get('true', 0),
            'Bicycle': data['AccidentInvolvingBicycle'].value_counts().get('true', 0),
            'Motorcycle': data['AccidentInvolvingMotorcycle'].value_counts().get('true', 0)
        }
        stats['vehicle_involvement'] = vehicle_stats
        
        print("\n----- Vehicle Involvement -----")
        for vehicle, count in vehicle_stats.items():
            percentage = (count / stats['total_accidents'] * 100).round(1)
            print(f"Accidents involving {vehicle}: {count} ({percentage}%)")
        
        # Temporal analysis
        if 'AccidentYear' in data.columns:
            year_counts = data['AccidentYear'].value_counts().sort_index()
            stats['yearly_distribution'] = year_counts.to_dict()
            
            print("\n----- Yearly Distribution -----")
            for year, count in year_counts.items():
                print(f"Year {year}: {count} accidents")
        
        if 'AccidentMonth' in data.columns:
            month_counts = data['AccidentMonth'].value_counts().sort_index()
            stats['monthly_distribution'] = month_counts.to_dict()
            
            print("\n----- Monthly Distribution -----")
            for month, count in month_counts.items():
                month_name = data[data['AccidentMonth'] == month]['AccidentMonth_en'].iloc[0]
                print(f"Month {month} ({month_name}): {count} accidents")
        
        if 'AccidentWeekDay' in data.columns:
            weekday_counts = data['AccidentWeekDay'].value_counts()
            stats['weekday_distribution'] = weekday_counts.to_dict()
            
            print("\n----- Weekday Distribution -----")
            for weekday, count in weekday_counts.items():
                weekday_name = data[data['AccidentWeekDay'] == weekday]['AccidentWeekDay_en'].iloc[0]
                print(f"{weekday} ({weekday_name}): {count} accidents")
        
        if 'AccidentHour' in data.columns:
            # Convert to numeric for statistical calculations
            hour_numeric = pd.to_numeric(data['AccidentHour'], errors='coerce')
            
            hour_stats = {
                'mean': hour_numeric.mean().round(2),
                'median': hour_numeric.median(),
                'std': hour_numeric.std().round(2),
                'min': hour_numeric.min(),
                'max': hour_numeric.max()
            }
            stats['hour_statistics'] = hour_stats
            
            print("\n----- Accident Hour Statistics -----")
            print(f"Mean hour: {hour_stats['mean']}")
            print(f"Median hour: {hour_stats['median']}")
            print(f"Standard deviation: {hour_stats['std']}")
            print(f"Hour range: {hour_stats['min']} - {hour_stats['max']}")
            
            # Hour distribution
            hour_counts = data['AccidentHour'].value_counts().sort_index()
            stats['hourly_distribution'] = hour_counts.to_dict()
            
            print("\n----- Hourly Distribution -----")
            for hour, count in hour_counts.items():
                print(f"Hour {hour}: {count} accidents")
        
        # Road type analysis
        if 'RoadType' in data.columns:
            road_counts = data['RoadType'].value_counts()
            stats['road_type_distribution'] = road_counts.to_dict()
            
            print("\n----- Road Type Distribution -----")
            for road_type, count in road_counts.head(5).items():
                road_name = data[data['RoadType'] == road_type]['RoadType_en'].iloc[0]
                percentage = (count / stats['total_accidents'] * 100).round(1)
                print(f"{road_type} ({road_name}): {count} accidents ({percentage}%)")
            
            if len(road_counts) > 5:
                print(f"... and {len(road_counts) - 5} more road types")
        
        # Canton/Municipality analysis
        if 'CantonCode' in data.columns:
            canton_counts = data['CantonCode'].value_counts()
            stats['canton_distribution'] = canton_counts.to_dict()
            
            print("\n----- Canton Distribution -----")
            for canton, count in canton_counts.items():
                percentage = (count / stats['total_accidents'] * 100).round(1)
                print(f"Canton {canton}: {count} accidents ({percentage}%)")
        
        return stats
    
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
                    marker=dict(size=8),
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
            map_style="open-street-map",
            map=dict(
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

# Calculate and print statistics
processor.calculate_statistics()

# Visualize the data as scatter points
print("Generating scatter map...")
processor.visualize_data(viz_type='scatter')

# Visualize the data as a heatmap
print("Generating heatmap...")
processor.visualize_data(viz_type='heatmap')
