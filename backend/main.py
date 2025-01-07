from fastapi import FastAPI, HTTPException
from backend.core import methods as m1
from backend.config import pdict, DATA_PATHS
from backend.src.user_profile.user_profile_service import router as auth_router
import pandas as pd

# Initialize FastAPI
app = FastAPI()

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

