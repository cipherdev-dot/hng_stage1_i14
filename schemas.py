from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime

class CreateProfileRequest(BaseModel):
    name: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().lower()

class ProfileResponse(BaseModel):
    id: str
    name: str
    gender: str
    gender_probability: float
    sample_size: int
    age: int
    age_group: str
    country_id: str
    country_probability: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfileListItem(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    age_group: str
    country_id: str
    
    class Config:
        from_attributes = True

class SuccessResponse(BaseModel):
    status: str = "success"
    data: ProfileResponse

class ExistingProfileResponse(BaseModel):
    status: str = "success"
    message: str = "Profile already exists"
    data: ProfileResponse

class ProfileListResponse(BaseModel):
    status: str = "success"
    count: int
    data: List[ProfileListItem]

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
