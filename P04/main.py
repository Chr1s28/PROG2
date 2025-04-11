from P04.downloader import DatasetDownloader
from P04.dataset_processor import AccidentDataProcessor


url = "https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte/download/RoadTrafficAccidentLocations.parquet"

downloader = DatasetDownloader(url)
raw_dataset = downloader.load_as_dataframe()

processor = AccidentDataProcessor(raw_dataset)
stats = processor.calculate_statistics()
processor.visualize_data(viz_type='scatter')
processor.visualize_data(viz_type='heatmap')
