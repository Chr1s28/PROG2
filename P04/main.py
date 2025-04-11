import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

class DatasetDownloader:
    """
    A class to download datasets with a timeout functionality to prevent
    multiple downloads within a specified time period.
    """
    
    def __init__(self, url, timeout_seconds=10):
        """
        Initialize the DatasetDownloader with a URL and timeout period.
        
        :param url: The URL of the dataset to download
        :type url: str
        :param timeout_seconds: Minimum seconds between downloads
        :type timeout_seconds: int
        """
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.last_download_time = None
        self.local_filename = os.path.basename(url)
    
    def _can_download(self):
        """
        Check if enough time has passed since the last download.
        
        :return: True if download is allowed, False otherwise
        :rtype: bool
        """
        if self.last_download_time is None:
            return True
            
        elapsed_time = datetime.now() - self.last_download_time
        return elapsed_time.total_seconds() >= self.timeout_seconds
    
    def download(self, force=False):
        """
        Download the dataset if the timeout period has passed.
        
        :param force: Force download even if timeout hasn't passed
        :type force: bool
        :return: Path to the downloaded file or None if download was skipped
        :rtype: str or None
        """
        if not force and not self._can_download():
            remaining = self.timeout_seconds - (datetime.now() - self.last_download_time).total_seconds()
            print(f"Download timeout in effect. Try again in {remaining:.1f} seconds or use force=True.")
            return None
            
        print(f"Downloading dataset from {self.url}")
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        
        with open(self.local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        self.last_download_time = datetime.now()
        print(f"Download completed: {self.local_filename}")
        return self.local_filename
    
    def load_as_dataframe(self, force_download=False):
        """
        Download the dataset and load it as a pandas DataFrame.
        
        :param force_download: Force download even if timeout hasn't passed
        :type force_download: bool
        :return: DataFrame containing the dataset or None if download was skipped
        :rtype: pandas.DataFrame or None
        """
        filename = self.download(force=force_download)
        if filename is None:
            if os.path.exists(self.local_filename):
                print(f"Using existing file: {self.local_filename}")
                return pd.read_parquet(self.local_filename)
            return None
            
        return pd.read_parquet(filename)


# Example URL for Zurich traffic accident locations
url = "https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte/download/RoadTrafficAccidentLocations.parquet"
