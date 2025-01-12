from fastapi import FastAPI, HTTPException, Depends
from backend.core import methods as m1
from backend.config import pdict, DATA_PATHS
from backend.src.user_profile.user_profile_service import router as auth_router
from backend.src.user_profile.user_profile_repositories import UserRepository
import pandas as pd
from backend.src.charging_station_search.charging_station_search_service import StationSearchService, StationRepository
from backend.src.charging_station_rating.charging_station_rating_service import RatingRepository
from backend.src.charging_station_rating.charging_station_rating_management import RatingManagement
from backend.src.charging_station_search.charging_station_search_management import InvalidPostalCodeException
from backend.db.mongo_client import user_collection

app = FastAPI()

# Initialize repositories
user_repository = UserRepository(user_collection)
station_repository = StationRepository()
rating_repository = RatingRepository()
rating_management = RatingManagement()

# Include Authentication Routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"message": "Welcome to the Charging Station Backend API"}

@app.get("/data", tags=["Data"])
async def get_processed_data():
    """Fetch preprocessed data from backend."""

    try:
        # Load raw data
        df_geodat_plz = pd.read_csv(DATA_PATHS['geodata_berlin_plz'], sep=';')
        df_lstat = pd.read_excel(DATA_PATHS['ladesaeulenregister'], header=10)
        df_residents = pd.read_csv(DATA_PATHS['plz_einwohner'])

        # Data preprocessing
        gdf_lstat = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
        gdf_lstat3 = m1.count_plz_occurrences(gdf_lstat)
        gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

        # Standardize column names
        gdf_lstat3.rename(columns={"PLZ": "Postleitzahl"}, inplace=True)
        gdf_residents2.rename(columns={"PLZ": "Postleitzahl"}, inplace=True)

        # Serialize geometry to WKT for frontend compatibility
        gdf_lstat3["geometry"] = gdf_lstat3["geometry"].apply(lambda geom: geom.wkt if geom else None)
        gdf_residents2["geometry"] = gdf_residents2["geometry"].apply(lambda geom: geom.wkt if geom else None)

        return {
            "geodat_plz": df_geodat_plz.to_dict(orient="records"),
            "lstat": gdf_lstat3.to_dict(orient="records"),
            "residents": gdf_residents2.to_dict(orient="records")
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"File not found: {e.filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stations/search/{postal_code}", tags=["Charging Stations"])
async def search_stations(postal_code: str):
    """
    Search for charging stations by postal code.
    """
    try:
        service = StationSearchService(repository=station_repository)
        result = await service.search_by_postal_code(postal_code) 
        return {
            "stations": [
                {
                    "id": station.id,
                    "postal_code": station.postal_code.value,
                    "availability_status": station.availability_status,
                    "location": station.location,
                }
                for station in result.stations
            ],
            "stations_found": result.event.stations_found,
            "timestamp": result.event.timestamp.isoformat(),
        }
    except InvalidPostalCodeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/stations/{station_id}/rate", tags=["Charging Stations"])
async def rate_station(station_id: str, rating_value: int, comment: str, current_user=Depends(user_repository.get_user_by_id)):
    """
    Rate a charging station.
    """
    try:
        rating_management = RatingManagement()  # Create an instance of RatingManagement
        result = await rating_management.handle_create_rating(
            userSession=current_user,
            user_id=str(current_user["_id"]),
            station_id=station_id,
            rating_value=rating_value,
            comment=comment,
        )
        return {"message": "Rating submitted successfully", "rating": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stations/{station_id}/ratings", tags=["Charging Stations"])
async def get_station_ratings(station_id: str):
    """
    Get ratings for a specific charging station.
    """
    try:
        ratings = await rating_repository.get_ratings_by_station(station_id)
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    