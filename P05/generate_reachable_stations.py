import json
import time
from P05.api_service import ApiService
from requests.exceptions import RequestException

# --- Configuration ---
HOME_STATION = "Zürich HB"

# List of potential stations to check
potential_border_stations = [
    # Germany
    "Stuttgart Hbf", "Freiburg(Breisgau) Hbf", "Konstanz", "Singen(Hohentwiel)",
    "Karlsruhe Hbf", "Ulm Hbf", "Lörrach Hbf", "Waldshut", "Offenburg", "Mannheim Hbf",
    "Augsburg Hbf", "Lindau-Reutin", "Lindau-Insel",
    # France
    "Paris Gare de Lyon", "Mulhouse", "Lyon Part-Dieu", "Annemasse", "Bellegarde(Ain)", "Besançon Viotte",
    "Strasbourg", "Colmar", "Belfort-Montbéliard TGV", "Dijon Ville", "Chambéry - Challes-les-Eaux",
    "Grenoble", "Pontarlier", "St Louis La Chaussée", "Nancy",
    # Italy
    "Milano Centrale", "Domodossola", "Como S. Giovanni", "Tirano", "Varese", "Gallarate",
    "Chiasso", "Torino Porta Susa", "Torino Porta Nuova", "Verona Porta Nuova", "Lecco",
    "Genoa Piazza Principe", "Bolzano/Bozen",
    # Austria
    "Bregenz", "Feldkirch", "Innsbruck Hbf", "Salzburg Hbf", "Bludenz", "Landeck-Zams",
    # Liechtenstein
    "Schaan-Vaduz",
    # Switzerland
    "St. Margrethen",
]

OUTPUT_FILENAME = "reachable_stations.json"
# --- End Configuration ---

def generate_reachable_list(origin: str, destinations: list[str]) -> list[dict]:
    """
    Checks reachability from origin to each destination using the API
    and returns details of reachable stations.
    """
    api = ApiService()
    reachable_stations = []
    print(f"Checking reachability from '{origin}' to {len(destinations)} potential stations...")

    for i, dest in enumerate(destinations):
        print(f"[{i+1}/{len(destinations)}] Checking: {dest} ... ", end="")
        try:
            connection = api.get_next_connection(origin, dest)

            if connection:
                station_data = connection.to.station.model_dump(include={"id", "name", "coordinate"})
                reachable_stations.append(station_data)
                print("Reachable")
            else:
                print("Not directly reachable")

        except RequestException as e:
            print(f"NETWORK ERROR checking {dest}: {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR checking {dest}: {e}")

        time.sleep(0.3) # Small delay between requests

    return reachable_stations

def write_to_json(data: list[dict], filename: str):
    """Writes the list of station data to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully wrote {len(data)} reachable stations to '{filename}'")
        if len(data) < 30:
             print(f"\nWarning: Found only {len(data)} reachable stations.")
             print("Consider expanding the 'potential_border_stations' list.")

    except IOError as e:
        print(f"\nError writing to file '{filename}': {e}")
    except TypeError as e:
        print(f"\nError serializing data to JSON: {e}")


if __name__ == "__main__":
    reachable_data = generate_reachable_list(HOME_STATION, potential_border_stations)
    if reachable_data:
        write_to_json(reachable_data, OUTPUT_FILENAME)
    else:
        print("\nNo reachable stations found with the current list.")
