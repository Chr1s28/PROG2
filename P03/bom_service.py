from typing import Any

import requests as rq
from pydantic import BaseModel, Field, PositiveInt, field_validator
from requests.adapters import HTTPAdapter, Retry
from rich.console import Console
from rich.table import Table as RichTable


class Car(BaseModel):
    """
    Represents a car with various components and their prices.
    """

    steering_wheel: PositiveInt | None = Field(None, alias="Lenkrad")
    tires: PositiveInt | None = Field(None, alias="Reifen")
    rear_rack: PositiveInt | None = Field(None, alias="Hutablage")
    chassis: PositiveInt | None = Field(None, alias="Fahrgestell")
    gearbox: PositiveInt | None = Field(None, alias="Getriebe")
    wheel_suspension: PositiveInt | None = Field(None, alias="Radaufhängung")
    ignition_system: PositiveInt | None = Field(None, alias="Zündanlage")

    @field_validator("*", mode="before")
    def validate_pos_int(cls, value: Any) -> int | None:
        """
        Validates that the input value is a positive integer.

        :param value: The value to validate.
        :type value: Any
        :return: The validated positive integer or None if invalid.
        :rtype: int | None
        """

        try:
            value = int(value)
        except (ValueError, TypeError):
            return None
        else:
            return value if value > 0 else None

    def print_bom_table(self) -> None:
        """
        Prints the Bill of Materials (BOM) table for the car.
        """

        table = RichTable(title="Bill of Materials")
        table.add_column("Material")
        table.add_column("Preis")

        model_dict = self.model_dump(exclude_none=True, by_alias=True)

        for i, (key, value) in enumerate(model_dict.items()):
            end_section = i == len(model_dict) - 1
            table.add_row(key, str(value), end_section=end_section)

        table.add_row("Total", str(sum(model_dict.values())))

        Console().print(table)


class BomService:
    """
    Service for fetching car data from a remote server (up to 5 retries).

    :param url: The URL of the remote server.
    :type url: str
    """

    def __init__(self, url: str) -> None:
        self.url = url
        self.session = rq.Session()
        self.session.mount(
            "http://",
            HTTPAdapter(
                max_retries=Retry(
                    total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
                )
            ),
        )

    @staticmethod
    def _decode_keys(json: dict[str, Any]) -> dict[str, Any]:
        """
        Decodes JSON keys from Latin-1 to UTF-8.

        :param json: The JSON dictionary with keys to decode.
        :type json: dict[str, Any]
        :return: The JSON dictionary with decoded keys.
        :rtype: dict[str, Any]
        """

        for key in list(json.keys()):
            try:
                json[key.encode("latin-1").decode("utf-8")] = json.pop(key)
            except UnicodeDecodeError:
                pass

        return json

    def get_car(self) -> Car:
        """
        Fetches car data from the remote server and returns a Car object.

        :return: A Car object with the fetched data.
        :rtype: Car
        """

        resp = self.session.get(self.url)

        json = resp.json()
        json = self._decode_keys(json)

        car = Car(**json)
        return car


if __name__ == "__main__":
    bom_service = BomService("http://160.85.252.87/")
    car = bom_service.get_car()
    car.print_bom_table()
