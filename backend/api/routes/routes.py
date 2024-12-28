from fastapi import APIRouter, HTTPException
from db import station_collection
from api.schemas import StationSchema
from bson.objectid import ObjectId

router = APIRouter()

@router.get("/stations", response_model=list[StationSchema])
async def get_stations():
    stations = await station_collection.find().to_list(100)
    return stations

@router.post("/stations", response_model=StationSchema)
async def add_station(station: StationSchema):
    result = await station_collection.insert_one(station.dict())
    return {**station.dict(), "_id": str(result.inserted_id)}
