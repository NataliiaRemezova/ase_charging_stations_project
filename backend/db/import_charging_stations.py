import pandas as pd
from backend.db.mongo_client import station_collection  # MongoDB connection
from backend.core.methods import preprop_lstat
from backend.config import pdict, DATA_PATHS
import asyncio

async def index_charging_stations():
    """
    Manually index charging stations from the dataset into MongoDB.
    """
    try:
        # Load the source data (charging station dataset)
        file_path = DATA_PATHS['ladesaeulenregister']  # Ensure correct dataset path
        df_lstat = pd.read_excel(file_path, header=10)  # Adjust header row if needed
        
        # Load geometry data (e.g., geodata for PLZ mapping)
        df_geodata = pd.read_csv(DATA_PATHS['geodata_berlin_plz'], sep=';')

        # Preprocess the data
        processed_data = preprop_lstat(df_lstat, df_geodata, pdict)
        if processed_data is None or processed_data.empty:
            print("No valid data to process.")
            return

        # Prepare MongoDB documents
        documents = []
        for _, row in processed_data.iterrows():
            document = {
                "postal_code": str(row["PLZ"]),
                "availability_status": True,  # Assuming default availability for new data
                "location": {
                    "latitude": row["Breitengrad"],
                    "longitude": row["Längengrad"],
                    "description": row.get("Location", "Unknown Location"),  # Example additional field
                },
                "power_kw": row.get("KW", 0),  # Include power rating if available
            }
            documents.append(document)

        # Insert into MongoDB
        if documents:
            result = await station_collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} charging stations into MongoDB.")
        else:
            print("No documents to insert.")

    except Exception as e:
        print(f"Error during indexing: {e}")


if __name__ == "__main__":
    asyncio.run(index_charging_stations())
