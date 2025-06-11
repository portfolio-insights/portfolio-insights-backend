"""
Defines Pydantic data models for API requests and responses.

This module includes schemas used for validation and serialization
in FastAPI endpoints.
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


# Response schemas
class AlertResponse(BaseModel):  # Alert creation/deletion response
    message: str
    new_alert_id: Optional[int] = None
    deleted_alert_id: Optional[int] = None
