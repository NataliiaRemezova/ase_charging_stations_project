from fastapi import FastAPI, HTTPException, Depends, Body
from typing import Optional
from backend.utilities import methods as m1
from backend.config import pdict, DATA_PATHS
from backend.src.user_profile.user_profile_service import router as auth_router
from backend.src.user_profile.user_profile_repositories import UserRepository
import pandas as pd
from backend.src.charging_station_search.charging_station_search_service import StationSearchService, StationRepository
from backend.src.charging_station_rating.charging_station_rating_service import RatingRepository
from backend.src.charging_station_rating.charging_station_rating_management import Rating, RatingManagement
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
    """
    Root endpoint for API health check.
    Returns a welcome message.
    """
    return {"message": "Welcome to the Charging Station Backend API"}

@app.get("/data", tags=["Data"])
async def get_processed_data():
    """
    Fetch preprocessed data from backend.
    
    This endpoint loads data from predefined paths, processes it,
    and returns structured data for frontend compatibility.
    
    Returns:
        dict: A dictionary containing processed geolocation, charging station,
              and resident population data.
    """

    try:
        # Load raw data
        df_geodat_plz = pd.read_csv(DATA_PATHS['geodata_berlin_plz'], sep=';')
        df_lstat = pd.read_excel(DATA_PATHS['ladesaeulenregister'], header=10)
        df_residents = pd.read_csv(DATA_PATHS['plz_einwohner'])

        # Data preprocessing
        gdf_lstat = m1.preprocess_lstat(df_lstat, df_geodat_plz, pdict)
        gdf_lstat3 = m1.count_plz_occurrences(gdf_lstat)
        gdf_residents2 = m1.preprocess_resid(df_residents, df_geodat_plz, pdict)

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
    
    Args:
        postal_code (str): The postal code to search for charging stations.
    
    Returns:
        dict: A dictionary containing a list of charging stations and metadata.
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
                    "name": station.name,  # Include station name
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
async def rate_station(
    station_id: str,
    rating_data: dict = Body(...),
    user_id: Optional[str] = None,  # Make user_id optional
    current_user=Depends(user_repository.get_user_by_id)
):
    """
    Rate a charging station.
    
    Args:
        station_id (str): ID of the charging station.
        rating_data (dict): Contains rating value and optional comment.
        user_id (Optional[str]): User ID, defaults to None.
        current_user: Authenticated user session.
    
    Returns:
        dict: A confirmation message and rating details.
    """

    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = user_id or str(current_user["_id"])  # Use query or token-based user_id
    try:
        rating_management = RatingManagement()
        result = await rating_management.handle_create_rating(
            username=current_user["username"],
            user_id=user_id,
            station_id=station_id,
            rating_value=rating_data.get("rating_value"),
            comment=rating_data.get("comment"),
        )
        return {"message": "Rating submitted successfully", "rating": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/stations/{station_id}/availability", tags=["Charging Stations"])
async def rate_station(
    station_id: str,
    user_id: Optional[str] = None,
    current_user=Depends(user_repository.get_user_by_id)
):
    """
    Change an availability of the station
    
    Args:
        station_id (str): ID of the charging station.
        user_id (Optional[str]): User ID, defaults to None.
        current_user: Authenticated user session.
    
    Returns:
        dict: A confirmation message.
    """

    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = user_id or str(current_user["_id"])  # Use query or token-based user_id
    try:
        update_result = await station_repository.update_availability_status(station_id)
        return {"message": "Availability changed successfully", "availability_status": update_result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stations/{station_id}/ratings", tags=["Charging Stations"])
async def get_station_ratings(station_id: str):
    """
    Get ratings for a specific charging station.
    
    Args:
        station_id (str): The ID of the charging station.
    
    Returns:
        list: A list of rating records.
    """
    try:
        ratings = await rating_repository.get_ratings_by_station(station_id)
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.put("/ratings/{rating_id}", tags=["Ratings"])
async def update_rating(
            rating_id: str,
            rating_data: dict = Body(...),
            user_id: Optional[str] = None
        ):
    """
    Update a specific rating based on its ID.
    
    Args:
        rating_id (str): The ID of the rating to update.
    
    Returns:
        dict: The updated rating record.
    
    Raises:
        HTTPException: If the rating does not exist or if validation fails.
    """
    try:
        if user_id is not None:
            if rating_repository.get_rating_by_id(rating_id)["user_id"] == user_id:
                rating_value=rating_data.get("rating_value"),
                comment=rating_data.get("comment"),
                updated_rating = await rating_repository.update_rating(
                    rating_id=rating_id,
                    comment=comment,
                    rating_value=rating_value
                )
            else:
                raise HTTPException(status_code=401, detail="The action of this user is not allowed")
        else:
            raise HTTPException(status_code=401, detail="User is not authorized")
        if not updated_rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        return updated_rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/ratings/{rating_id}", tags=["Ratings"])
async def delete_rating(
            rating_id: str,
            user_id: Optional[str] = None):
    """
    Delete a specific rating based on its ID.
    
    Args:
        rating_id (str): The ID of the rating to delete.
    
    Returns:
        dict: A success message.
    
    Raises:
        HTTPException: If the rating does not exist.
    """
    try:
        if user_id is not None:
            if rating_repository.get_rating_by_id(rating_id)["user_id"] == user_id:
                success = await rating_repository.delete_rating(rating_id)
            else:
                raise HTTPException(status_code=401, detail="The action of this user is not allowed")
        else:
            raise HTTPException(status_code=401, detail="User is not authorized")
        if not success:
            raise HTTPException(status_code=404, detail="Rating not found")
        return {"message": "Rating deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")