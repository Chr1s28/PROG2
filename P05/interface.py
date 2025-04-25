import json
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.distance import distance as geopy_distance # Use alias to avoid name clash

from P05.api_service import ApiService
from P05.models import Connection, Location, Coordinates # Import Coordinates


class Interface:
    def __init__(self):
        self.api_service = ApiService()
        self.local_providers = self._load_local_providers()
        self.covered_stations = self.read_covered_stations() # Load stations after providers

        # --- Initialize Nominatim Geocoder ---
        # !!! IMPORTANT: Replace with your Nominatim instance details and user agent !!!
        nominatim_domain = 'YOUR_NOMINATIM_DOMAIN_OR_IP' # e.g., 'localhost:8080' or 'nominatim.example.com'
        app_user_agent = 'YourApp/1.0 (your@email.com)' # Replace with your app name/contact
        try:
            self.geolocator = Nominatim(domain=nominatim_domain, user_agent=app_user_agent, timeout=10)
            print(f"Initialized geolocator for domain: {nominatim_domain}")
        except Exception as e:
            print(f"FATAL: Could not initialize Nominatim geolocator: {e}")
            self.geolocator = None # Ensure geolocator is None if init fails
        # --- End Initialization ---

    def _load_local_providers(self):
        """Loads the local provider data from the JSON file."""
        try:
            with open("local_providers.json", encoding="utf8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: local_providers.json not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Could not decode local_providers.json.")
            return {}

    def read_covered_stations(self):
        """Reads and parses the reachable station data."""
        try:
            with open("reachable_stations.json", encoding="utf8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                 raise ValueError("reachable_stations.json should contain a list.")
            return [Location(**station) for station in data]
        except FileNotFoundError:
            print("Error: reachable_stations.json not found. Please generate it first.")
            return []
        except json.JSONDecodeError:
            print("Error: Could not decode reachable_stations.json.")
            return []
        except Exception as e:
             print(f"Error parsing station data in reachable_stations.json: {e}")
             return []

    def _calculate_distance(self, loc1: Location | None, loc2: Location | None) -> float:
        """Calculates geodesic distance in km between two Locations using geopy."""
        if not loc1 or not loc2 or not loc1.coordinate or not loc2.coordinate:
            return 0.0

        coords1 = (loc1.coordinate.latitude, loc1.coordinate.longitude)
        coords2 = (loc2.coordinate.latitude, loc2.coordinate.longitude)
        return geopy_distance(coords1, coords2).km

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

    def get_intermediate_connections_by_bearing(
        self, origin_obj: Location, destination_obj: Location
    ) -> list[Connection]:
        """Finds intermediate connections based on bearing (+/- 20 degrees)."""
        if not origin_obj or not destination_obj:
             return []

        connection_stations = []
        for covered_station in self.covered_stations:
            if covered_station and covered_station.coordinate:
                deviation = self.angular_deviation(origin_obj, destination_obj, covered_station)
                if deviation <= 20:
                    connection_stations.append(covered_station)

        intermediate_connections = []
        for station in connection_stations:
            # Fetch connection from actual origin name to candidate station name
            conn = self.api_service.get_next_connection(origin_obj.name, station.name)
            if conn:
                intermediate_connections.append(conn)

        return intermediate_connections

    def get_local_provider(self, location: Location) -> dict[str, str] | None:
        """Looks up the local transport provider based on location coordinates using Nominatim."""
        if not self.geolocator:
            print("Error: Geolocator not initialized.")
            return None
        if not location or not location.coordinate or not self.local_providers:
            return None

        try:
            coords = (location.coordinate.latitude, location.coordinate.longitude)
            # Use Nominatim for reverse geocoding
            location_info = self.geolocator.reverse(coords, language='en', exactly_one=True)

            if location_info and location_info.raw.get('address'):
                address = location_info.raw['address']
                country_code = address.get('country_code')
                if country_code:
                    # Use uppercase country code consistent with local_providers.json
                    return self.local_providers.get(country_code.upper())
                else:
                    print(f"Warning: Could not determine country code for {location.name} from Nominatim.")
                    return None
            else:
                print(f"Warning: No address details found in Nominatim reverse lookup for {location.name}.")
                return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
             print(f"Error: Nominatim reverse geocoding failed: {e}")
             return None
        except Exception as e:
            print(f"Error during reverse geocoding or provider lookup: {e}")
            return None

    def _display_connection_option(
        self,
        conn: Connection,
        option_index: int,
        origin_obj: Location,
        destination_obj: Location,
        total_distance: float,
        is_direct: bool
    ):
        """Formats and prints the details for a single connection option."""
        if not conn: return

        intermediate_station = conn.to.station
        covered_distance = self._calculate_distance(origin_obj, intermediate_station)
        percentage = (covered_distance / total_distance * 100) if total_distance > 0 else 0

        header = f"--- Option {option_index} {'(Direct)' if is_direct else '(Intermediate via '+intermediate_station.name+')'} ---"
        print(f"\n{header}")
        print(f"  Travel:     {conn.from_.station.name} -> {intermediate_station.name}")
        print(f"  Departure:  {conn.from_.departure.strftime('%Y-%m-%d %H:%M')} (Platform: {conn.from_.platform or 'N/A'})")
        print(f"  Arrival:    {conn.to.arrival.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Duration:   {conn.duration}")

        if not is_direct and total_distance > 0:
            print(f"  Coverage:   Approx. {covered_distance:.1f} km ({percentage:.0f}% of total distance)")

        if not is_direct:
            provider = self.get_local_provider(intermediate_station)
            print(f"  Next Step:  To continue towards {destination_obj.name},")
            if provider:
                print(f"              search connections from {intermediate_station.name} using {provider['name']} ({provider['url']})")
            else:
                print(f"              search connections from {intermediate_station.name} (Provider lookup failed)")
        print("-" * len(header))


    def execute(self):
        """Main execution loop for the user interface."""
        if not self.covered_stations:
             print("Cannot proceed without reachable station data.")
             return

        origin_name = input("Where are you? ")
        destination_name = input("Where do you want to go to? ")

        origin_obj = self.api_service.get_location(origin_name)
        if not origin_obj:
            print(f"Error: Could not find origin station '{origin_name}'. Please check spelling.")
            return

        destination_obj = self.api_service.get_location(destination_name)
        if not destination_obj:
            print(f"Info: Destination '{destination_name}' not found in transport API. Trying geocoding...")
            if not self.geolocator:
                 print("Error: Geolocator not initialized, cannot find coordinates for destination.")
                 return

            try:
                # Use Nominatim geocode as fallback
                geo_location = self.geolocator.geocode(destination_name)
                if geo_location:
                    print(f"Info: Found coordinates for '{destination_name}' via geocoding.")
                    # Create a minimal Location object for calculations
                    destination_coords = Coordinates(type='WGS84', latitude=geo_location.latitude, longitude=geo_location.longitude)
                    # Use a placeholder ID (e.g., -1) as it's not from the transport API
                    destination_obj = Location(id=-1, name=destination_name, coordinate=destination_coords)
                else:
                    print(f"Error: Could not find coordinates for destination '{destination_name}' via geocoding either.")
                    return
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                 print(f"Error: Nominatim geocoding failed for destination: {e}")
                 return
            except Exception as e:
                 print(f"Error during destination geocoding: {e}")
                 return

        # Proceed only if we have a valid destination_obj (either from API or geocoding)
        if not destination_obj:
             # This case should ideally not be reached due to prior returns, but added for safety
             print("Error: Failed to determine destination location.")
             return


        print("\nSearching for connections...")
        # Use origin_obj.name which is guaranteed to be from the API
        direct_connection = self.get_direct_connection(origin_obj.name, destination_name)

        connections_to_display = []
        is_direct = False

        if direct_connection:
            print("Direct connection found:")
            connections_to_display = [direct_connection]
            is_direct = True
        else:
            print("No direct connection found. Searching for intermediate options...")
            connections_to_display = self.get_intermediate_connections_by_bearing(
                origin_obj, destination_obj
            )
            if not connections_to_display:
                print("No suitable intermediate connections found via reachable border stations.")
                return

            print("\nPossible intermediate connections:")

        total_distance = self._calculate_distance(origin_obj, destination_obj)
        if total_distance > 0:
            print(f"(Approx. total distance: {total_distance:.1f} km)")

        for i, conn in enumerate(connections_to_display):
            self._display_connection_option(
                conn=conn,
                option_index=i + 1,
                origin_obj=origin_obj,
                destination_obj=destination_obj,
                total_distance=total_distance,
                is_direct=is_direct
            )

if __name__ == "__main__":
    interface = Interface()
    # Only run execute if the geolocator was initialized successfully
    if interface.geolocator:
        interface.execute()
    else:
        print("Exiting due to geolocator initialization failure.")
