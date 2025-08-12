# Placer.ai POI Analytics Dashboard

A full-stack web application for analyzing Big Box Store Point of Interest (POI) data. Built with FastAPI backend and React frontend.

## Features

### Core Features
- **Paginated POI Table**: Browse through POI data with pagination controls
- **Advanced Filtering**: Filter by chain name, DMA, category, city, state, and open/closed status
- **Search Functionality**: Search across multiple fields with autocomplete suggestions
- **Summary Statistics**: Real-time dashboard showing key metrics
- **Responsive Design**: Clean, modern UI built with Material-UI

### Enhanced Features
- **CSV Export**: Export filtered data to CSV format
- **Analytics Dashboard**: Interactive charts showing:
  - Chain performance analysis
  - DMA distribution visualization
  - Sales per visitor metrics
- **Autocomplete Search**: Smart search suggestions across multiple fields
- **Real-time Filtering**: All filters and statistics update dynamically

## Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: SQL toolkit and Object Relational Mapper
- **SQLite**: Lightweight file-based database
- **Pydantic**: Data validation and serialization
- **Pandas**: Data export and CSV processing
- **Uvicorn**: ASGI server for development and production

### Frontend
- **React 18**: Modern React with TypeScript
- **Material-UI**: Google's Material Design components
- **Recharts**: Responsive charts and visualizations
- **Axios**: HTTP client for API calls

## Project Structure

```
placer-ai-assignment/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── utils/           # Helper utilities
│   │   ├── database.py      # Database configuration
│   │   └── __init__.py
│   ├── scripts/
│   │   └── migrate_csv_to_db.py  # Data migration script
│   ├── tests/              # Test suite
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── poi_database.db     # SQLite database (auto-created)
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client services
│   │   ├── types/          # TypeScript type definitions
│   │   ├── App.tsx         # Main React component
│   │   └── index.tsx       # React entry point
│   ├── public/
│   └── package.json        # Node.js dependencies
├── Bigbox Stores Metrics.csv  # Source data file
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Quick Start

To run the application, you need to start both the backend and frontend manually in separate terminals.

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
*Or alternatively:*
```bash
python main.py
```

The backend API will be available at `http://localhost:8000`

**Note**: The application will automatically load CSV data into a SQLite database on first startup if no data exists.

### Frontend Setup

Open a **new terminal** and follow these steps:

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend application will be available at `http://localhost:3000`

### Running the Complete Application

1. **Terminal 1** (Backend):
```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn main:app --reload
```

2. **Terminal 2** (Frontend):
```bash
cd frontend
npm start
```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Documentation

Once the backend is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **OpenAPI schema**: http://localhost:8000/openapi.json

### Key Endpoints

- `GET /api/v1/pois` - Get paginated POI data with filtering
- `GET /api/v1/pois/summary` - Get summary statistics
- `GET /api/v1/pois/export/csv` - Export filtered data as CSV
- `GET /api/v1/pois/analytics/chain-performance` - Chain performance data
- `GET /api/v1/pois/analytics/dma-distribution` - DMA distribution data
- `GET /api/v1/pois/autocomplete` - Search autocomplete suggestions

## Usage

### Filtering Data
- Use the filter panel to narrow down POI data by various criteria
- Filters are applied in real-time to both the table and summary statistics
- Multiple filters can be combined for precise data selection

### Search Functionality
- Use the search bar to find POIs by name, chain, city, or address
- Autocomplete suggestions appear as you type
- Search works across multiple fields simultaneously

### Analytics
- Switch to the "Analytics" tab to view data visualizations
- Charts show chain performance, DMA distribution, and other insights
- All charts are interactive and responsive

### Export Data
- Click the "Export CSV" button in the POI table header
- Exported file includes all currently filtered data
- CSV format is compatible with Excel and other data analysis tools
- Large datasets are handled gracefully with streaming export

## Data Schema

The application works with POI data containing the following fields:

| Field | Description | Type |
|-------|-------------|------|
| entity_id | Unique POI identifier | String |
| name | Venue name | String |
| chain_name | Brand/chain name | String |
| sub_category | Business category | String |
| city | City location | String |
| state_name | State name | String |
| dma | Designated Market Area | Integer |
| foot_traffic | Total visits | Integer |
| sales | Total sales revenue | Float |
| avg_dwell_time_min | Average visit duration | Float |
| is_open | Current operational status | Boolean |

## Performance Considerations

- **Pagination**: Large datasets are paginated for optimal performance
- **Lazy Loading**: Charts and analytics load independently
- **Efficient Filtering**: Server-side filtering reduces data transfer
- **Caching**: Filter options are cached to reduce API calls

## Future Enhancements

Potential improvements that could be added:

1. **Map Visualization**: Interactive map showing POI locations
2. **Advanced Analytics**: Time-series analysis, predictive models
3. **User Authentication**: Role-based access control
4. **Real-time Updates**: WebSocket connections for live data
5. **Advanced Export**: Excel files with multiple sheets
6. **Dashboards**: Customizable dashboard layouts
7. **Data Import**: Upload and analyze custom datasets

## Development Notes

- The backend uses dependency injection for the data service
- Frontend components are modular and reusable
- TypeScript provides type safety throughout the application
- Material-UI ensures consistent, accessible design
- Error handling is implemented at all levels

## License

This project was created for the Placer.ai technical assignment.
