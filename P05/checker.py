import json

from P05.api_service import ApiService
from P05.models import Connection


def write_to_file(result_dict, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)


def check_connection(origin: str, border_stations: list[str]) -> list[Connection]:
    result = []

    for dest in border_stations:
        print(dest)
        connection = ApiService().get_next_connection(origin, dest)

        if connection:
            result.append(connection.to.station.model_dump(include=["id", "name", "coordinate"]))

    return result
