from datetime import datetime, time, date
from pytz import timezone, UTC

from flask import request


def get_user_timezone():
    """
    Fetch the user's timezone from headers or use a default value.

    Returns:
        The pytz timezone object.
    """
    user_timezone = request.headers.get("TimeZone", "UTC")
    try:
        return timezone(user_timezone)
    except Exception:
        return timezone("UTC")


def calculate_due_status(due_date_utc, user_tz, item_type):
    """
    Calculate the due status based on the due date and the current date.

    Args:
        due_date_utc (datetime): The due date in UTC.
        user_tz (pytz.timezone): The user's timezone.

    Returns:
        str: The due status ('VENCIDO', 'VENCE HOJE', 'A VENCER', etc.).
    """
    # If the item is 'Income' or 'Rendimentos', skip due_status calculation
    if item_type in ["income", "Rendimentos"]:
        return ""  # No due_status for income items

    # If the item is 'paid-expenses' or 'Pago', return 'PAGO'
    if item_type in ["paid-expenses", "Pago"]:
        return "PAGO"

    # Check if due_date_utc is a date object (without time)
    if isinstance(due_date_utc, date) and not isinstance(
        due_date_utc, datetime
    ):
        # Convert it to a datetime object, assuming midnight as the time
        due_date_utc = datetime.combine(due_date_utc, time.min).replace(
            tzinfo=UTC
        )

    # Ensure due_date_utc is timezone aware
    if due_date_utc.tzinfo is None:
        due_date_utc = due_date_utc.replace(tzinfo=UTC)

    # Convert due_date to user's local timezone
    due_date_local = due_date_utc.astimezone(user_tz).date()

    # Get the current date in the user's timezone
    today = datetime.now(UTC).astimezone(user_tz).date()

    # Calculate the difference in days
    days_difference = (due_date_local - today).days

    if days_difference < 0:
        return "VENCIDO"
    elif days_difference == 0:
        return "VENCE HOJE"
    elif days_difference == 1:
        return "VENCE AMANHÃ"
    elif days_difference <= 3:
        return f"A VENCER EM {days_difference} DIAS"
    else:
        return "A PAGAR"
