from motor.motor_asyncio import AsyncIOMotorClient
import os

# Environment Variable for MongoDB URL
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# MongoDB Client
client = AsyncIOMotorClient(MONGO_URL)
db = client["berlin_bezirke_db"]

# Collections
user_collection = db.get_collection("users")
station_collection = db.get_collection("charging_stations")
rating_collection = db.get_collection("ratings")
