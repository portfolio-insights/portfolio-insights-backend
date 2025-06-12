"""
Manage stock price alerts through interaction with the PostgreSQL database.
"""

from src import database
from src.schemas import Alert
from src.logging import logger
from datetime import datetime, timezone
from typing import List, Dict, Any


def search(user_id: int, search_term: str) -> List[Dict[str, Any]]:
    """
    Search stock price alerts by a search term.
    """
    logger.debug(
        "Fetching alerts for user #%s and search_term: %s", user_id, search_term
    )
    # Use wildcards (%) to match prefix, suffix, or substring
    ilike_argument = "%" + search_term + "%"
    with database.connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM alerts WHERE ticker ILIKE %s AND user_id = %s;",
            (ilike_argument, user_id),
        )
        # Extract column names from the result metadata
        keys = [column[0] for column in cur.description]
        all_alerts = cur.fetchall()
        logger.info("Retrieved %d alerts", len(all_alerts))
        # Format results as list of dictionaries for JSON compatibility
        return [dict(zip(keys, row)) for row in all_alerts]


def create(alert: Alert) -> int:
    """
    Create a new stock price alert.
    Note that the alert id will be automatically created in the database using SERIAL.
    """
    logger.debug("Creating alert...")

    # Convert Pydantic model to plain dict and set 'expired' status
    logger.debug("Transforming alert Pydantic model to plain dict...")
    alert = alert.model_dump()
    if alert["expiration_time"]:
        alert["expired"] = False
    else:
        alert["expired"] = None

    # Insert alert into the database
    with database.connection.cursor() as cur:
        cur.execute(
            """
                INSERT INTO alerts (user_id, ticker, price, direction, expired, expiration_time)
                VALUES (%(user_id)s, %(ticker)s, %(price)s, %(direction)s, %(expired)s, %(expiration_time)s) RETURNING alert_id;
                """,
            alert,
        )
        database.connection.commit()
        new_alert_id = cur.fetchone()[0]
        logger.debug("Created alert #%s for user %s", new_alert_id, alert["user_id"])
        return new_alert_id


def delete(id: int) -> None:
    """
    Delete a stock price alert by id.
    """
    logger.debug("Deleting alert #%s...", id)
    with database.connection.cursor() as cur:
        cur.execute("DELETE FROM alerts WHERE alert_id = %s RETURNING alert_id;", (id,))
        database.connection.commit()
    logger.debug("Deletion successful")


# THE EVALUATE FUNCTION WILL NOT WORK BECAUSE IT HAS NOT YET BEEN REFACTORED TO CONNECT TO MAIN.GO INSTEAD OF MARKET.PY
def evaluate() -> None:
    """
    Evaluate all alerts against stock prices to determine if alert should be triggered.
    """
    # Fetch active, untriggered alerts from the database
    with database.connection.cursor() as cur:
        cur.execute(
            """
                SELECT alert_id, ticker, price, direction
                FROM alerts
                WHERE triggered = false AND expired = false;
                """
        )
        alerts = cur.fetchall()

    # Avoid redundant API calls by caching stock prices
    cache = {}
    for id, ticker, price, direction in alerts:
        # Get stock price (use cached value if available)
        if ticker in cache:
            stock_price = cache[ticker]
        else:
            stock_price = market.stock_price(ticker)
            cache[ticker] = stock_price

        # Trigger alert if stock price meets condition
        if (direction == "below" and price > stock_price) or (
            direction == "above" and price < stock_price
        ):
            trigger(id)


def trigger(id: int) -> None:
    """
    Triggers an alert based on its id.
    """
    logger.debug("Triggering alert #%s...", id)
    with database.connection.cursor() as cur:
        trigger_time = datetime.now(timezone.utc)
        cur.execute(
            """
                UPDATE alerts
                SET triggered = true, triggered_time = %s, expired = NULL, expiration_time = NULL
                WHERE alert_id = %s;
                """,
            (trigger_time, id),
        )
        database.connection.commit()
    logger.debug("Alert triggered at %s", trigger_time)
