/project-root
│
├── backend/                  # FastAPI Backend
│   ├── api/                  # API Endpoints
│   │   ├── routes/
│   │   │   ├── charging_station.py  # API endpoints for charging station
│   │   │   ├── residents.py         # API endpoints for residents
│   │   ├── dependencies.py          # Shared dependencies (e.g., DB, security)
│   │   ├── __init__.py
│   │
│   ├── core/                 # Core settings & configurations
│   │   ├── config.py         # App settings
│   │   ├── database.py       # MongoDB Connection
│   │   ├── security.py       # Authentication, security configurations
│   │   ├── __init__.py
│   │
│   ├── models/               # Database Models
│   │   ├── charging_station.py
│   │   ├── residents.py
│   │   ├── __init__.py
│   │
│   ├── repositories/         # Data Access Logic
│   │   ├── charging_station_repository.py
│   │   ├── residents_repository.py
│   │   ├── __init__.py
│   │
│   ├── services/             # Business Logic
│   │   ├── charging_station_service.py
│   │   ├── residents_service.py
│   │   ├── __init__.py
│   │
│   ├── schemas/              # Pydantic Schemas
│   │   ├── charging_station_schema.py
│   │   ├── residents_schema.py
│   │   ├── __init__.py
│   │
│   ├── tests/                # Backend Tests
│   │   ├── test_routes.py
│   │   ├── test_services.py
│   │   ├── test_repositories.py
│   │   ├── __init__.py
│   │
│   ├── main.py               # FastAPI Entry Point
│   ├── requirements.txt
│   ├── __init__.py
│
├── frontend/                 # Streamlit Frontend
│   ├── pages/                # Streamlit Pages
│   │   ├── home.py
│   │   ├── charging_stations.py
│   │   ├── residents.py
│   │
│   ├── components/           # Reusable Streamlit Components
│   │   ├── maps.py
│   │   ├── charts.py
│   │
│   ├── config.py             # Streamlit Configurations
│   ├── streamlit_app.py      # Frontend Entry Point
│   ├── requirements.txt
│   ├── __init__.py
│
├── datasets/                 # Data Files
│   ├── geodata_berlin_dis.csv
│   ├── geodata_berlin_plz.csv
│   ├── Ladesaeulenregister_SEP.xlsx
│   ├── plz_einwohner.csv
│
├── shared/                   # Shared Utilities
│   ├── helper_tools.py       # Helper functions and utilities
│   ├── methods.py            # Data processing methods
│   ├── __init__.py
│
├── tests/                    # Global Tests
│   ├── backend/
│   │   ├── test_api.py
│   │   ├── test_services.py
│   ├── frontend/
│   │   ├── test_pages.py
│   │   ├── test_components.py
│   ├── __init__.py
│
├── docs/                     # Documentation
│   ├── installation_guide.txt
│   ├── README.md
│
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── streamlit.Dockerfile
└── LICENSE
