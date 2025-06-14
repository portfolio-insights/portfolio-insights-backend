"""
Development begun using the FastAPI "First Steps" tutorial.
Reference: https://fastapi.tiangolo.com/tutorial/first-steps/

Activate the backend virtual environment by running the shell command:
source venv/bin/activate

Start the server by running the shell command:
fastapi dev server.py
"""

from src.logging import logger

logger.info("Starting Portfolio Insights backend")
logger.info("Importing modules...")

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import httpx
from src import alerts, database, users
from src.schemas import (
    Alert,
    Token,
    UserLogin,
    AlertResponse,
    UserRegister,
    UserResponse,
)
from typing import List, Dict
import os
from dotenv import load_dotenv

logger.info("Modules loaded")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()
logger.info(f"Environment loaded:")
for key, value in os.environ.items():
    logger.info(f"   {key} = {value}")

cors_origins = os.getenv("CORS_ORIGINS").split(",")
go_api_url = os.getenv("GO_API_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------#

##### Authentication Endpoints #####


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint that returns a JWT token for authenticated users.
    """
    try:
        # Verify user credentials, raise error if user not found or password is incorrect
        user_info = users.verify_credentials(form_data.username, form_data.password)
        # If no error was raised, create access token
        access_token = users.create_access_token(data=user_info)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as http_exc:
        # Re-raise the HTTP exception with its original status code and detail
        raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
        )


@app.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Token | UserResponse],
)
async def register(user_data: UserRegister):
    """
    Register a new user and return a JWT token along with user information.
    """
    try:
        # Register the user
        user_info = users.register_user(user_data.username, user_data.password)
        # Create access token for the new user
        access_token = users.create_access_token(data=user_info)
        return {
            "token": {"access_token": access_token, "token_type": "bearer"},
            "user": user_info,
        }
    except HTTPException as http_exc:
        raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration",
        )


# ------------------------------------------------------------------------#

##### Protected Endpoints #####


# Get alerts matching optional search_term
@app.get("/alerts", response_model=List[Dict])
async def search_alerts(
    search_term: str = "",
    current_user: Dict[str, str | int] = Depends(users.get_user_from_token),
) -> List[Dict]:
    try:
        return alerts.search(current_user["user_id"], search_term)
    except Exception as e:
        logger.error(f"Error searching alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint to create a new alert
@app.post("/alerts", status_code=status.HTTP_201_CREATED, response_model=AlertResponse)
def create_alert(
    alert: Alert,
    current_user: Dict[str, str | int] = Depends(users.get_user_from_token),
) -> AlertResponse:
    # Ensure user can only create alerts for themselves
    # Realistically this is prevented by the UI because a user can only see their own alerts
    if alert.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create alerts for other users",
        )
    try:
        alert_id = alerts.create(alert)
        return AlertResponse(
            message="Alert created successfully", new_alert_id=alert_id
        )
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Delete alert by ID (query parameter)
@app.delete("/alerts", response_model=AlertResponse)
def delete_alert(
    id: int, current_user: Dict[str, str | int] = Depends(users.get_user_from_token)
) -> AlertResponse:
    try:
        alerts.delete(id)
        return AlertResponse(message="Alert deleted successfully", deleted_alert_id=id)
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ------------------------------------------------------------------------#

##### Lifespan Events #####


# On startup, open database connection
@app.on_event("startup")
def startup() -> None:
    logger.info("Opening database connection")
    return database.init()


# On shutdown, close database connection
@app.on_event("shutdown")
def shutdown() -> None:
    logger.info("Closing database connection")
    return database.close()


# ------------------------------------------------------------------------#

##### General #####


# Root
@app.get("/")
async def root() -> str:
    return "Hello World"


# Health check for uptime monitoring
@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


# Health check for database and market connections
@app.get("/health/deep")
async def health_check_deep() -> Dict[str, str | bool]:

    logger.info("Testing database connection...")
    db_ok = database.ping()

    logger.info("Testing market connection...")
    endpoint = "/health"
    url = go_api_url + endpoint
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
        response.raise_for_status()
        market_ok = True
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"Go microservice health check failed: {e}")
        market_ok = False

    return {
        "status": "ok" if db_ok and market_ok else "fail",
        "database connection": db_ok,
        "market connection": market_ok,
    }


# Temporary endpoint for manual testing
@app.get("/test")
async def test():
    return True


# ------------------------------------------------------------------------#

##### Market Connections #####


# Endpoint to return stock price history
@app.get("/stocks")
async def get_stock_info(
    ticker: str, startDate: str, interval: str
) -> List[Dict[str, str | float]]:
    endpoint = "/stocks"
    query = f"?ticker={ticker}&startDate={startDate}&interval={interval}"
    url = go_api_url + endpoint + query
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail="Error from Go service"
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Ticker not found")


@app.get("/check-alert")
async def check_alert(
    ticker: str, price: float, direction: str
) -> Dict[str, str | bool]:
    endpoint = "/check-alert"
    query = f"?ticker={ticker}&price={price}&direction={direction}"
    url = go_api_url + endpoint + query
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("message", "Error from Go service")
        except Exception:
            detail = "Error from Go service"
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=502, detail="Market service unavailable")
