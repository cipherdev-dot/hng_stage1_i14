# HNG Stage 1 - Profile API

A FastAPI-based REST API that fetches profile data from external APIs (Genderize, Agify, Nationalize), applies classification logic, and stores the results in a SQLite database.

## Features

- Create profiles by fetching data from 3 external APIs
- Idempotent profile creation (duplicate names return existing profile)
- Retrieve single profile by ID
- List all profiles with optional filtering (gender, country_id, age_group)
- Delete profiles
- Full error handling with proper HTTP status codes
- CORS enabled for cross-origin requests

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd hng_stage1
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Create Profile
**POST** `/api/profiles`

Request:
```json
{
  "name": "ella"
}
```

Response (201):
```json
{
  "status": "success",
  "data": {
    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
    "name": "ella",
    "gender": "female",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 46,
    "age_group": "adult",
    "country_id": "DRC",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}
```

### 2. Get Single Profile
**GET** `/api/profiles/{id}`

Response (200):
```json
{
  "status": "success",
  "data": { ... }
}
```

### 3. Get All Profiles
**GET** `/api/profiles?gender=male&country_id=NG`

Response (200):
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "id": "id-1",
      "name": "emmanuel",
      "gender": "male",
      "age": 25,
      "age_group": "adult",
      "country_id": "NG"
    }
  ]
}
```

### 4. Delete Profile
**DELETE** `/api/profiles/{id}`

Response: 204 No Content

## Error Responses

All errors follow this format:
```json
{
  "status": "error",
  "message": "<error message>"
}
```

- **400**: Missing or empty name
- **404**: Profile not found
- **422**: Invalid type
- **502**: External API returned invalid response

## Technology Stack

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database
- **httpx**: Async HTTP client for external API calls
- **uuid7**: UUID v7 generation
- **Pydantic**: Data validation

## Project Structure

```
hng_stage1/
├── main.py          # FastAPI app and endpoints
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic request/response schemas
├── database.py      # Database configuration
├── services.py      # External API integration
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Deployment

This application can be deployed to:
- Vercel
- Railway
- Heroku
- AWS
- Any platform supporting Python/FastAPI

Make sure to set the appropriate environment variables and database configuration for production.

## License

MIT
