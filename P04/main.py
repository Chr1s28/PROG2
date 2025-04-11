import os
import time
import requests
import pandas as pd
import re
import plotly.graph_objects as go
from pyproj import Transformer
from datetime import datetime, timedelta

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
        self.cache_seconds = cache_seconds
    
    def download(self, force=False):
        """
        Download the dataset using file-based caching.
        
        :param force: Force download even if cached version exists
        :type force: bool
        :return: Path to the downloaded file
        :rtype: str
        """
        # Check if file exists and is recent enough
        should_download = force or not self._is_cache_valid()
        
        if should_download:
            print(f"Downloading dataset from {self.url}")
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            
            with open(self.local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Download completed: {self.local_filename}")
        else:
            print(f"Using cached file: {self.local_filename} (last modified: {self._get_file_age_str()})")
            
        return self.local_filename
    
    def _is_cache_valid(self):
        """
        Check if the cached file exists and is recent enough.
        
        :return: True if cache is valid, False otherwise
        :rtype: bool
        """
        if not os.path.exists(self.local_filename):
            return False
            
        # Get file modification time
        file_mtime = os.stat(self.local_filename).st_mtime
        current_time = time.time()
        
        # Check if file is recent enough
        return (current_time - file_mtime) < self.cache_seconds
    
    def _get_file_age_str(self):
        """
        Get a human-readable string of when the file was last modified.
        
        :return: String representation of file age
        :rtype: str
        """
        if not os.path.exists(self.local_filename):
            return "file does not exist"
            
        file_mtime = os.stat(self.local_filename).st_mtime
        mtime_dt = datetime.fromtimestamp(file_mtime)
        return mtime_dt.strftime("%Y-%m-%d %H:%M:%S")
    
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
    def __init__(self, dataframe):
        """
        Initialize the processor with a pandas DataFrame.
        
        :param dataframe: The accident dataset
        :type dataframe: pandas.DataFrame
        """

        self.raw_data = dataframe

        self.remove_language_columns()
    
    def remove_language_columns(self):
        """
        Remove columns with language-specific suffixes (_de, _fr, _it)
        
        :return: DataFrame with language columns removed
        :rtype: pandas.DataFrame
        """

        all_columns = self.raw_data.columns.tolist()
        
        columns_to_keep = []
        for col in all_columns:
            if not re.search(r'_(de|fr|it)$', col):
                columns_to_keep.append(col)
        
        self.processed_data = self.raw_data[columns_to_keep].copy()
    
    def calculate_statistics(self):
        """
        Calculate and print various statistics about the dataset
        
        :return: Dictionary containing the calculated statistics
        :rtype: dict
        """
        data = self.processed_data
        stats = {}
        
        stats['total_accidents'] = len(data)
        print("\n===== ACCIDENT DATASET STATISTICS =====")
        print(f"Total number of accidents: {stats['total_accidents']}")
        
        severity_counts = data['AccidentSeverityCategory'].value_counts()
        severity_percentages = (severity_counts / stats['total_accidents'] * 100).round(1)
        stats['severity_distribution'] = severity_counts.to_dict()
        
        print("\n----- Accident Severity -----")
        for severity, count in severity_counts.items():
            severity_name = data[data['AccidentSeverityCategory'] == severity]['AccidentSeverityCategory_en'].iloc[0]
            print(f"{severity_name}: {count} accidents ({severity_percentages[severity]}%)")
        
        vehicle_columns = {
            'Pedestrian': 'AccidentInvolvingPedestrian',
            'Bicycle': 'AccidentInvolvingBicycle',
            'Motorcycle': 'AccidentInvolvingMotorcycle'
        }
        
        vehicle_stats = {}
        print("\n----- Vehicle Involvement -----")
        
        for vehicle_type, column in vehicle_columns.items():
            count = sum(1 for value in data[column] if value is True)
            vehicle_stats[vehicle_type] = count
            
            percentage = round(count / stats['total_accidents'] * 100, 1)
            print(f"Accidents involving {vehicle_type}: {count} ({percentage}%)")
        
        stats['vehicle_involvement'] = vehicle_stats
        
        year_counts = data['AccidentYear'].value_counts().sort_index()
        stats['yearly_distribution'] = year_counts.to_dict()
        
        print("\n----- How many per year -----")
        for year, count in year_counts.items():
            print(f"Year {year}: {count} accidents")
        
        weekday_counts = data['AccidentWeekDay'].value_counts()
        stats['weekday_distribution'] = weekday_counts.to_dict()
        
        print("\n----- How many on weekdays -----")
        for weekday, count in weekday_counts.items():
            weekday_name = data[data['AccidentWeekDay'] == weekday]['AccidentWeekDay_en'].iloc[0]
            print(f"{weekday_name}: {count} accidents")
        
        hour_numeric = pd.to_numeric(data['AccidentHour'], errors='coerce')
        
        hour_stats = {
            'mean': round(hour_numeric.mean(), 2),
            'median': hour_numeric.median(),
        }
        stats['hour_statistics'] = hour_stats
        
        print("\n----- Accident Hours -----")
        print(f"Mean hour: {hour_stats['mean']}")
        print(f"Median hour: {hour_stats['median']}")
        
        road_counts = data['RoadType'].value_counts()
        stats['road_type_distribution'] = road_counts.to_dict()
        
        print("\n----- Road Types -----")
        for road_type, count in road_counts.head(5).items():
            road_name = data[data['RoadType'] == road_type]['RoadType_en'].iloc[0]
            percentage = round(count / stats['total_accidents'] * 100, 1)
            print(f"{road_name}: {count} accidents ({percentage}%)")
        
    def visualize_data(self, viz_type):
        """
        Visualize accident locations with Plotly.
        
        :param viz_type: Type of visualization ('scatter' or 'heatmap')
        :type viz_type: str
        :return: Plotly figure object
        :rtype: plotly.graph_objects.Figure
        """
        
        viz_data = self.processed_data.copy()
        
        # CHLV95 to WGS84
        transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
        
        coordinates = [
            transformer.transform(row.AccidentLocation_CHLV95_E, row.AccidentLocation_CHLV95_N) 
            for _, row in viz_data.iterrows()
        ]
        
        viz_data['longitude'] = [coord[0] for coord in coordinates]
        viz_data['latitude'] = [coord[1] for coord in coordinates]
        
        fig = go.Figure()
        
        if viz_type.lower() == 'scatter':
            for severity in viz_data['AccidentSeverityCategory'].unique():
                category_data = viz_data[viz_data['AccidentSeverityCategory'] == severity]
                
                fig.add_trace(go.Scattermap(
                    lat=category_data['latitude'],
                    lon=category_data['longitude'],
                    mode='markers',
                    marker=dict(size=8),
                    name=severity,
                    hoverinfo='text'
                ))
            
        elif viz_type.lower() == 'heatmap':
            fig.add_trace(go.Densitymap(
                lat=viz_data['latitude'],
                lon=viz_data['longitude'],
                z=[1] * len(viz_data),
                radius=10,
                colorscale='Hot',
                hoverinfo='none'
            ))
        
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
processor.calculate_statistics()
#processor.visualize_data(viz_type='scatter')
#processor.visualize_data(viz_type='heatmap')
