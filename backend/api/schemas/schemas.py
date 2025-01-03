from pydantic import BaseModel

class StationSchema(BaseModel):
    name: str
    latitude: float
    longitude: float
    power: float
