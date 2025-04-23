import json
import math

import reverse_geocoder as rg

from P05.api_service import ApiService
from P05.models import Connection, Location


class Interface:
    def __init__(self):
        self.covered_stations = self.read_covered_stations()
        self.api_service = ApiService()

    def read_covered_stations(self):
        with open("test.json", encoding="utf8") as f:
            data = json.load(f)

        return [Location(**station) for station in data]

    def bearing(self, origin: Location, destination: Location) -> float:
        lat1 = math.radians(origin.coordinate.latitude)
        lon1 = math.radians(origin.coordinate.longitude)
        lat2 = math.radians(destination.coordinate.latitude)
        lon2 = math.radians(destination.coordinate.longitude)
        d_lon = lon2 - lon1
        x = math.cos(lat2) * math.sin(d_lon)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)

        return (math.degrees(math.atan2(x, y)) + 360) % 360

    def angular_deviation(self, origin: Location, destination: Location, candidate: Location) -> float:
        b_od = self.bearing(origin, destination)
        b_oc = self.bearing(origin, candidate)

        return min(math.fabs(b_od - b_oc), 360 - math.fabs(b_od - b_oc))

    def get_direct_connection(self, origin: str, destination: str) -> Connection | None:
        connection = self.api_service.get_next_connection(origin, destination)
        return connection

    def get_intermediate_connections(self, origin: str, destination: str) -> list[Connection]:
        origin_obj = self.api_service.get_location(origin)
        destination_obj = self.api_service.get_location(destination)

        connection_stations = []
        for covered_station in self.covered_stations:
            if self.angular_deviation(origin_obj, destination_obj, covered_station) <= 20:
                connection_stations.append(covered_station)

        return [
            self.api_service.get_next_connection(origin, connection_station.name)
            for connection_station in connection_stations
        ]

    def get_local_provider(self, location: Location) -> dict[str, str]:
        country_cd = rg.get((location.coordinate.latitude, location.coordinate.longitude))["cc"]

        with open("local_providers.json", encoding="utf8") as f:
            local_providers = json.load(f)

        return local_providers[country_cd]

    def execute(self):
        origin = input("Where are you? ")
        destination = input("Where do you want to go to? ")

        direct_connection = self.get_direct_connection(origin, destination)
        connections = (
            [direct_connection] if direct_connection else self.get_intermediate_connections(origin, destination)
        )

        print("Your intermediate connections are:")
        for connection in connections:
            print(connection)
            print("Find more information here:")
            print(self.get_local_provider(connection.to.station))
