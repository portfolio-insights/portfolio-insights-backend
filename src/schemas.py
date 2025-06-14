"""
Defines Pydantic data models for API requests and responses.

This module includes schemas used for validation and serialization in FastAPI endpoints.
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


# Used in POST /alerts for automatic validation and parsing
class Alert(BaseModel):
    user_id: int
    ticker: str
    price: float
    direction: str
    expiration_time: Optional[datetime]  # ISO 8601 string will be automatically parsed

    # Validate direction to be either 'above' or 'below'
    # Also enforced in database
    @field_validator("direction")
    @classmethod  # Required because field_validator expects a class as its first argument
    def validate_direction(cls, v):
        if v not in ["above", "below"]:
            raise ValueError('direction must be either "above" or "below"')
        return v

    # Validate ticker to have valid length
    # Also enforced in database
    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v):
        if not 1 <= len(v) <= 10:
            raise ValueError("ticker must be between 1 and 10 characters")
        return v.upper()  # Normalize to uppercase

    # Validate expiration time is in the future
    @field_validator("expiration_time")
    @classmethod
    def validate_expiration_time(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError("expiration time must be in the future")
        return v


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str

    # Validate username length
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not 2 <= len(v) <= 30:
            raise ValueError("username must be between 2 and 30 characters")
        return v

    # Validate password length
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not 8 <= len(v) <= 50:
            raise ValueError("password must be between 8 and 50 characters")
        return v


# Returned on successful user registration
class UserResponse(BaseModel):
    user_id: int
    username: str
    created_at: int  # Unix timestamp

    # created_at must be an int in order to be serialized to JSON for JWT
    # mode="before" required because created_at is passed in as a datetime object, and so attempting to save it in a datetime field will cause an error
    @field_validator("created_at", mode="before")
    @classmethod
    def convert_datetime_to_int(cls, v):
        if isinstance(v, datetime):
            print("Converting datetime to int...")
            return int(v.timestamp())
        return v


# Response schemas
class AlertResponse(BaseModel):  # Alert creation/deletion response
    message: str
    new_alert_id: Optional[int] = None
    deleted_alert_id: Optional[int] = None
