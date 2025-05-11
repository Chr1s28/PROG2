import requests as rq
from requests.adapters import HTTPAdapter, Retry

from P05.models import Connection, Location


class ApiService:
    def __init__(self, retries: int = 5):
        self.session = rq.Session()
        retry = Retry(total=retries, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504], allowed_methods=["GET"])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.connections_url = "https://transport.opendata.ch/v1/connections"
        self.locations_url = "http://transport.opendata.ch/v1/locations"

    def get_next_connection(self, origin: str, destination: str) -> Connection | None:
        resp = self.session.get(
            self.connections_url,
            params={"from": origin, "to": destination, "limit": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("connections"):
            return Connection(**data["connections"][0])
        else:
            return None

    def get_location(self, location: str) -> Location | None:
        resp = self.session.get(
            self.locations_url, params={"query": location, "type": "station", "limit": 1}, timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("stations"):
            return Location(**data["stations"][0])
        else:
            return None
