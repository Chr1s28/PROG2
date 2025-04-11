import os
import time
from datetime import datetime

import requests
import pandas as pd


class DatasetDownloader:    
    def __init__(self, url, cache_seconds=10):
        """
        Initialize the DatasetDownloader with a URL and cache period.
        
        :param url: The URL of the dataset to download
        :type url: str
        :param cache_seconds: Seconds to keep the local file before re-downloading
        :type cache_seconds: int
        """
        
        self.url = url
        self.local_filename = os.path.basename(url)
        self.cache_seconds = cache_seconds
    
    def load_as_dataframe(self):
        """
        Download the dataset if older than cache and load it as a pandas DataFrame.
        
        :return: DataFrame containing the dataset
        :rtype: pandas.DataFrame
        """

        if os.path.exists(self.local_filename):
            file_mtime = os.stat(self.local_filename).st_mtime
            file_age = time.time() - file_mtime
            
            if file_age < self.cache_seconds:
                mtime_dt = datetime.fromtimestamp(file_mtime)
                time_str = mtime_dt.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Using cached file: {self.local_filename} (last modified: {time_str})")
                return pd.read_parquet(self.local_filename)
        
        response = requests.get(self.url)
        response.raise_for_status()
        
        with open(self.local_filename, 'wb') as f:
            f.write(response.content)
        print(f"Download completed: {self.local_filename}")
        
        return pd.read_parquet(self.local_filename)
