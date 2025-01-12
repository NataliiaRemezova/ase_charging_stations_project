import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATA_PATHS = {
    'geodata_berlin_plz': 'datasets/geodata_berlin_plz.csv',
    'ladesaeulenregister': 'datasets/Ladesaeulenregister_SEP.xlsx',
    'plz_einwohner': 'datasets/plz_einwohner.csv'
}

p                           = dict()
p['picklefolder']           = 'pickles'
# -----------------------------------

p['geocode']                = 'PLZ'

p["file_lstations"]         = "Ladesaeulenregister.csv"
# p["file_buildings"]         = "gebaeude.csv"
p["file_residents"]         = "plz_einwohner.csv"
# p["file_amounttraf"]        = "Verkehrsaufkommen.csv"

p["file_geodat_plz"]       = "geodata_berlin_plz.csv"
p["file_geodat_dis"]       = "geodata_berlin_dis.csv"

# p["gebaeude_filter"]        = ["Freistehendes Einzelgebäude", "Doppelhaushälfte"]

# -----------------------------------
pdict = p.copy()

