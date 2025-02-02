# Electric Charging Stations and Residents in Berlin
## Module: Advanced Software Engineering
**University Master Project - Berliner Hochschule für Technik**

## Authors - Group 19
- Shaheen Tasneem, 107279
- Immenroth Nina, 907261 
- Remezova Nataliia, 106606 
- Azimy Zabihullah, 945106
- Pandey Navnish, 106141

## Project Overview  
ChargeHub Berlin is a platform designed to help users locate electric charging stations in Berlin, visualize their distribution alongside population density, and manage interactions like ratings and reviews. Users can sign up, log in, search for charging stations by postal code, and check their availability in real time. The project integrates geospatial visualization with a robust backend for an optimal user experience.

## Installation
1. Clone the Repository;
2. Activate venv: 
- python -m venv venv

Windows:
- venv\Scripts\activate

Linux/MacOS:
- source venv/bin/activate
2. Install Dependencies:
- pip install -r requirements.txt
3. Set Up MongoDB: Install MongoDB Community Edition and ensure it is running, more information can be found in the MongoDB documentation.

### Usage
1. **Run the Backend (FastAPI)**
    - fastapi dev backend/main.py
    - python backend/db/import_charging_stations.py
2. **Run the Frontend**
    - streamlit run frontend/streamlit_app.py
3. **Run Tests**
    - pytest tests/ 
4. **Run Test Coverage**
    - coverage run --source=backend/src -m pytest backend/tests/
    - coverage report
    - coverage html

## Features
- **Interactive Heatmaps**: Visualize population density and charging station locations in Berlin.
- **Search by Postal Code**: Quickly find charging stations in specific areas with real-time availability indicators.
- **User Ratings & Reviews**: Submit and update ratings (1-5 stars) with optional comments.
- **User Authentication**: Secure sign-up, login, and profile management.
- **API Integration**: RESTful endpoints for data retrieval and management.

## Access
  - Frontend Application: http://localhost:8501
  - API Documentation: http://localhost:8000/docs

## License

This project is a closed university project and is not open for public use, modification, or distribution. Unauthorized use, reproduction, or distribution of any part of this project is strictly prohibited.

## Contributions

As this is a university project, external contributions are not accepted. If you are part of the project team and wish to make modifications, please follow the contribution guidelines.
