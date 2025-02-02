# Advanced Software Engineering

## Heatmaps: Electric Charging Stations and Residents in Berlin

**University Master Project by Group 19:**
## Team members
- Azimy Zabihullah
- Immenroth Nina
- Shaheen Tasneem
- Remezova Nataliia
- Pandey Navnish

## Table of Contents

- Project Overview
- Features
  - Part 1: Spatial Distribution Visualization
  - Part 2: Charging Station Management
- Installation & Setup
  - Install Dependencies
  - Set Up MongoDB
  - How to Run the Project
  - Testing
- Project Structure
- Usage
- Architecture and Design
  - Domain-Driven Design (DDD) Structure
  - Test-Driven Development (TDD)
  - Module Refactoring
- Final Result

   
## Project Overview  
This master project, developed as part of an advanced software engineering course, ChargeHub Berlin is a comprehensive platform designed to help users locate electric charging stations in Berlin, visualize their distribution alongside population density, and manage user interactions such as ratings and reviews. Built with a modern tech stack, this project combines geospatial visualization with robust backend services for an optimal user experience.


1. **Spatial Distribution Visualization (Heatmaps):**  
   An interactive Streamlit application that displays heatmaps of Berlin’s population density and the locations of electric charging stations. This visualization helps identify areas with high demand and potential gaps in infrastructure.

2. **User, Charging Station, and Search Management:**  
   A FastAPI-based backend integrated with MongoDB that provides RESTful endpoints for:
   - User registration, authentication, and profile management.
   - CRUD operations for charging stations including a robust rating system.
   - Searching for charging stations by postal code with interactive map results.

The project leverages Domain-Driven Design (DDD) principles and Test-Driven Development (TDD) methodologies to ensure a modular, scalable, and maintainable codebase.


## Features

### Part 1: Spatial Distribution Visualization
- **Heatmap Overlays**: Visualize population density and charging station locations across Berlin.
- **Interactive Maps**: Explore data layers using Streamlit's interactive interface.

### Part 2: Charging Station Management
- **Search by Postal Code**: Find available stations in specific areas with real-time availability indicators.
- **User Ratings & Reviews**: Rate stations (1-5 stars) and leave comments to share experiences.
- **User Authentication**: Secure sign-up, login, and profile management.
- **API Integration**: RESTful endpoints for data retrieval and management.


## Installation & Setup
### Install Dependencies
pip install -r requirements.txt

### Set Up MangoDB
Install MongoDB Community Edition

### How to run Project
1. **Run the Backend (FastAPI)**
    - fastapi dev backend/main.py
    - python backend/db/import_charging_stations.py

2. **Run the Frontend**
    - streamlit run frontend/streamlit_app.py

3. **Testing**
    - pytest tests/ 


## Project Structure
```
ase_charging_stations_project/
├── backend/               # FastAPI application
│   ├── db/               # MongoDB connection & data import
│   ├── src/              # Core logic (users, stations, ratings)
│   └── tests/            # Unit tests
├── frontend/             # Streamlit interface
│   ├── utils/            # Helper classes
│   └── streamlit_app.py  # Main app entry
├── datasets/             # GeoJSON and CSV data files
└── requirements.txt      # Python dependencies
```

## Usage
1. Access the App
    - Frontend: http://localhost:8501
    - Backend API Docs: http://localhost:8000/docs

2. Key Features
    - Home Page: Overview of stations and city-wide metrics.
    - Heatmaps: Toggle between population and station density layers.
    - Postal Code Search: Enter a Berlin postal code (e.g., 10115) to view stations.
    - Rate Stations: Log in to submit/update ratings (1-5 stars with optional comments).
    - User Profile: Edit username, email, or password after registration.

## Architecture and Design

### Domain-Driven Design (DDD) Structure
The project is organized around core business domains:
- **Entities:**  
  - `ChargingStation`: Represents a charging station with attributes like location, ratings, and status.
  - `UserProfile`: Represents a registered user.
- **Value Objects:**  
  - `PostalCode`: An immutable object handling postal code logic.
- **Domain Events:**  
  - Events such as `ChargingStationSearched` indicate state changes.
- **Repositories and Services:**  
  - Repositories (e.g., `UserRepository`, `StationRepository`) handle data access.
  - Services (e.g., `RatingService`, `StationSearchService`) encapsulate business logic.

### Test-Driven Development (TDD)
We followed TDD practices to build a robust system:
- **Test Plan:**  
  Defined test cases with clear **Given-When-Then** structures covering:
  - Creation, update, and deletion of ratings.
  - Edge cases (e.g., invalid input, non-existent ratings).
- **Implementation:**  
  Tests are written using `pytest` and `pytest_asyncio` to handle asynchronous operations. Some validations (such as user authentication) are performed at the API level.

### Module Refactoring and Project Structure
Refactoring improved modularity and maintainability:
- **Frontend (Streamlit):**  
  Handles all user interactions and data visualizations.
- **Backend (FastAPI):**  
  Organized into domains for charging stations, ratings, and user profiles.
- **Database Integration:**  
  Utilizes MongoDB with asynchronous access through the Motor library.

### Final Result
The streamlit app for our analysis can be viewed [Here](#here).
