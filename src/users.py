"""
Handle user authentication and session management.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status
from src import database
from src.logging import logger
import os

# JWT configuration
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-secret-key-here"
)  # TODO: Remove default in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with the given data and a 30-minute expiration time.
    """
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_credentials(username: str, password: str) -> Dict[str, str | int]:
    """
    Verify user credentials against the database.
    Returns dict with user_id and username if credentials are valid.
    Raises HTTPException if credentials are invalid.
    """
    with database.connection.cursor() as cur:
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()

        if not result:
            # 404 doesn't need auth headers as it's not an auth issue
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_id, stored_password = result

        # Simple password comparison (no hashing for MVP)
        if password == stored_password:
            return {"user_id": user_id, "username": username}

        # 401 includes auth headers to indicate Bearer token auth is required
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_from_token(token: str) -> Dict[str, str | int]:
    """
    Extract and verify user info from JWT token.
    Returns dict with user_id and username if token is valid.
    Raises HTTPException if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Check if token has expired
        expired = datetime.now(UTC).timestamp() > payload["exp"]
        if expired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
