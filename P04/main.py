import os
import requests_cache
import pandas as pd
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
        
        # Check if response was from cache
        if getattr(response, 'from_cache', False) and not force:
            print(f"Using cached response (no download needed)")
        else:
            print(f"Downloading fresh data")
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


# Example URL for Zurich traffic accident locations
url = "https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte/download/RoadTrafficAccidentLocations.parquet"
