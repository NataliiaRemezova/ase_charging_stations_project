import pandas as pd
from backend.db.mongo_client import station_collection  
from backend.core.methods import preprop_lstat
from backend.config import pdict, DATA_PATHS
import asyncio


def sanitize_value(value):
    """Sanitize a value by ensuring it's a string and handling NaN/None."""
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, str):
        if value.isspace():
            return None
        return value.strip()
    return str(value)  


async def index_charging_stations():
    """
    Manually index charging stations from the dataset into MongoDB.
    """
    try:
        # Drop the existing collection to avoid duplicates
        await station_collection.drop()
        print("Dropped existing charging_stations collection.")

        # Load the source data (charging station dataset)
        file_path = DATA_PATHS['ladesaeulenregister']
        df_lstat = pd.read_excel(file_path, header=10)

        # Load geometry data (e.g., geodata for PLZ mapping)
        df_geodata = pd.read_csv(DATA_PATHS['geodata_berlin_plz'], sep=';')

        # Preprocess the data
        processed_data = preprop_lstat(df_lstat, df_geodata, pdict)
        if processed_data is None or processed_data.empty:
            print("No valid data to process.")
            return

        # Prepare MongoDB documents
        documents = []
        for idx, row in processed_data.iterrows():
            # Fetch original fields from the raw dataset (df_lstat)
            raw_row = df_lstat.iloc[idx]

            # Sanitize critical fields
            provider = sanitize_value(raw_row.get("Betreiber")) or "Unknown Provider"
            street = sanitize_value(raw_row.get("Straße")) or "Unknown Street"
            house_number = sanitize_value(raw_row.get("Hausnummer")) or ""
            city = sanitize_value(raw_row.get("Ort")) or "Unknown City"
            postal_code = sanitize_value(row.get("PLZ"))

            # Skip rows with missing critical fields
            if not postal_code:
                print(f"Skipping row with missing postal code: {row}")
                continue

            # Handle missing Anzeigename (Karte)
            station_name = sanitize_value(raw_row.get("Anzeigename (Karte)"))
            if not station_name:
                station_name = f"{provider} - {street} {house_number}".strip()

            # Construct description
            location_description = f"{provider}, {street} {house_number}, {city}".strip(", ")

            document = {
                "postal_code": postal_code,
                "availability_status": True,
                "location": {
                    "latitude": row["Breitengrad"],
                    "longitude": row["Längengrad"],
                    "description": location_description,
                },
                "power_kw": row.get("KW", 0),
                "name": station_name,
                "metadata": {
                    "provider": provider,
                    "street": street,
                    "house_number": house_number,
                    "city": city,
                    "postal_code": postal_code,
                },
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
