from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)

class Coordinates(BaseConfigModel):
    type: str
    latitude: float = Field(validation_alias="x")
    longitude: float = Field(validation_alias="y")


class Location(BaseConfigModel):
    id: int
    name: str
    score: int | None = None
    coordinate: Coordinates
    distance: int | None = None
    icon: str | None = None


class Connection(BaseConfigModel):
    class From(BaseConfigModel):
        station: Location
        departure: datetime
        delay: int | None
        platform: str

    class To(BaseConfigModel):
        station: Location
        arrival: datetime
        delay: int | None
        platform: str | None

    from_: From = Field(alias="from")
    to: To
    duration: timedelta
