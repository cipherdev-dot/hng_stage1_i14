from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from datetime import datetime
from uuid_utils import uuid7


from database import get_db, init_db
from models import Profile
from schemas import (
    CreateProfileRequest, 
    SuccessResponse, 
    ExistingProfileResponse,
    ProfileResponse,
    ProfileListResponse,
    ProfileListItem,
    ErrorResponse
)
from services import fetch_profile_data, ExternalAPIError

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Custom exception handler for validation errors (400 instead of 422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": "Missing or empty name"}
    )

# Custom exception handler for external API errors (502)
@app.exception_handler(ExternalAPIError)
async def external_api_exception_handler(request: Request, exc: ExternalAPIError):
    return JSONResponse(
        status_code=502,
        content={"status": "error", "message": str(exc)}
    )

@app.post("/api/profiles", status_code=201)
async def create_profile(request: CreateProfileRequest, db: Session = Depends(get_db)):
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(Profile.name == request.name).first()
    
    if existing_profile:
        return {
            "status": "success",
            "message": "Profile already exists",
            "data": ProfileResponse.model_validate(existing_profile)
        }
    
    # Fetch data from external APIs
    profile_data = await fetch_profile_data(request.name)
    
    # Generate UUID v7
    profile_id = str(uuid7())

    
    # Create new profile
    new_profile = Profile(
        id=profile_id,
        name=profile_data["name"],
        gender=profile_data["gender"],
        gender_probability=profile_data["gender_probability"],
        sample_size=profile_data["sample_size"],
        age=profile_data["age"],
        age_group=profile_data["age_group"],
        country_id=profile_data["country_id"],
        country_probability=profile_data["country_probability"],
        created_at=datetime.utcnow()
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return {
        "status": "success",
        "data": ProfileResponse.model_validate(new_profile)
    }

@app.get("/api/profiles/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    
    return {
        "status": "success",
        "data": ProfileResponse.model_validate(profile)
    }

@app.get("/api/profiles")
def get_all_profiles(
    gender: str = None,
    country_id: str = None,
    age_group: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Profile)
    
    # Apply case-insensitive filters
    if gender:
        query = query.filter(Profile.gender.ilike(gender))
    if country_id:
        query = query.filter(Profile.country_id.ilike(country_id))
    if age_group:
        query = query.filter(Profile.age_group.ilike(age_group))
    
    profiles = query.all()
    
    profile_items = [ProfileListItem.model_validate(p) for p in profiles]
    
    return {
        "status": "success",
        "count": len(profile_items),
        "data": profile_items
    }

@app.delete("/api/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    
    db.delete(profile)
    db.commit()
    
    return None

# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": "Profile not found"}
    )
