# Football Heaven

A comprehensive football statistics and analytics platform for football fans who love data.

## Project Structure

- `python/`: Backend Python code including database operations and API
  - `db.py`: Database operations for football statistics
  - `api.py`: Flask API to serve statistics data
  - `constants.py`: Constants used in the database
- `frontend/`: React.js frontend
- `db/`: SQLite database files
- `csv/`: CSV data files with football statistics

## Technology Stack

### Backend
- Python with Flask for the API
- SQLite for data storage (with plans to migrate to PostgreSQL)
- CSV data processing

### Frontend
- React.js
- Material UI for UI components
- Chart.js for data visualization
- React Router for navigation

## Getting Started

### Backend Setup

1. Install Python requirements:
```
cd python
pip install -r requirements.txt
```

2. Start the Flask API server:
```
cd python
python api.py
```

The API will be available at http://localhost:5000/api

### Frontend Setup

1. Navigate to the frontend directory:
```
cd frontend/frontend
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm start
```

The frontend will be available at http://localhost:3000

## Features

- Team and player statistics
- Advanced passing, receiving, and rushing metrics
- Statistical comparisons between players and teams
- Historical data analysis
- Interactive data visualization

## Future Enhancements

- Migrate to PostgreSQL for better performance
- Add user authentication
- Implement advanced filtering and search capabilities
- Add more types of visualizations
- Include defensive statistics
- Develop mobile application

## Data Sources

The data comes from PFF (Pro Football Focus) statistics in CSV format.

## License

This project is for educational purposes.