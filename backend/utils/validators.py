import datetime


def validate_reservation_dates(checkin: str, checkout: str) -> tuple[bool, str]:
    """
    Validate that checkin is today or future, and checkout is after checkin.
    Returns (is_valid, error_message).
    """
    try:
        now = datetime.datetime.now().date()
        checkin_date = datetime.datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.datetime.strptime(checkout, '%Y-%m-%d').date()
    except ValueError:
        return False, "Dates must be in YYYY-MM-DD format."

    if checkin_date < now or checkout_date < now:
        return False, "Check-in and check-out dates must be in the future."
    if checkout_date <= checkin_date:
        return False, "Check-out date must be after check-in date."

    return True, ""
