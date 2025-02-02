import pandas as pd
from backend.db.mongo_client import station_collection  
from backend.utilities.methods import preprocess_lstat
from backend.config import pdict, DATA_PATHS
import asyncio


def sanitize_value(value):
    """
    Sanitize a given value by ensuring it is a string and handling cases of NaN, None, or empty strings.

    Args:
        value (any): The value to be sanitized. Can be of any data type.

    Returns:
        str | None: A sanitized string with leading and trailing whitespace removed,
                    or None if the input is NaN, None, or an empty/whitespace-only string.
    """
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, str):
        if value.isspace():
            return None
        return value.strip()
    return str(value)  


async def index_charging_stations():
    """
    Manually index charging stations from a dataset into MongoDB.

    This function performs the following steps:
    1. Drops the existing `charging_stations` collection in MongoDB to prevent duplicates.
    2. Loads the charging station dataset from an Excel file.
    3. Loads geographic data (e.g., postal code mappings) from a CSV file.
    4. Preprocesses and cleans the dataset.
    5. Iterates over processed data to construct valid MongoDB documents.
    6. Inserts the constructed documents into MongoDB.

    Raises:
        Exception: If any unexpected error occurs during the indexing process.

    Returns:
        None
    """
    try:
        await station_collection.drop()
        print("Dropped existing charging_stations collection.")

        file_path = DATA_PATHS['ladesaeulenregister']
        df_lstat = pd.read_excel(file_path, header=10)

        df_geodata = pd.read_csv(DATA_PATHS['geodata_berlin_plz'], sep=';')

        processed_data = preprocess_lstat(df_lstat, df_geodata, pdict)
        if processed_data is None or processed_data.empty:
            print("No valid data to process.")
            return

        documents = []
        for idx, row in processed_data.iterrows():
            raw_row = df_lstat.iloc[idx]

            provider = sanitize_value(raw_row.get("Betreiber")) or "Unknown Provider"
            street = sanitize_value(raw_row.get("Straße")) or "Unknown Street"
            house_number = sanitize_value(raw_row.get("Hausnummer")) or ""
            city = sanitize_value(raw_row.get("Ort")) or "Unknown City"
            postal_code = sanitize_value(row.get("PLZ"))

            if not postal_code:
                print(f"Skipping row with missing postal code: {row}")
                continue

            station_name = sanitize_value(raw_row.get("Anzeigename (Karte)"))
            if not station_name:
                station_name = f"{provider} - {street} {house_number}".strip()

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

        if documents:
            result = await station_collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} charging stations into MongoDB.")
        else:
            print("No documents to insert.")

    except Exception as e:
        print(f"Error during indexing: {e}")


if __name__ == "__main__":
    asyncio.run(index_charging_stations())
