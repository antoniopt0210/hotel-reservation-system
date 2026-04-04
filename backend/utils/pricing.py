"""
Pricing engine with dynamic pricing.
Supports per-night price overrides from Cassandra, weekend surcharges,
and seasonal multipliers. Falls back to room.base_price_usd when no
override exists.
"""
import datetime

TAX_RATE = 0.10

# Weekend surcharge (Fri/Sat nights)
WEEKEND_SURCHARGE = 0.15

# Seasonal multipliers — month number → multiplier
SEASONAL_MULTIPLIERS = {
    6: 1.20, 7: 1.25, 8: 1.20,   # summer peak
    12: 1.30, 1: 1.10,            # holiday season
}


def _get_cassandra_overrides(room_id: str, check_in: datetime.date, check_out: datetime.date) -> dict:
    """Fetch per-night price overrides from Cassandra. Returns {date_str: price}."""
    overrides = {}
    try:
        from db.cassandra_client import get_room_availability_month
        current = check_in
        fetched_months = set()
        while current < check_out:
            ym = current.strftime('%Y-%m')
            if ym not in fetched_months:
                fetched_months.add(ym)
                rows = get_room_availability_month(room_id, ym)
                for row in rows:
                    if row.get('price_override') is not None:
                        overrides[row['stay_date']] = row['price_override']
            current += datetime.timedelta(days=1)
    except Exception:
        pass
    return overrides


def calculate_price(room, check_in: datetime.date, check_out: datetime.date) -> dict:
    """
    Return a full price breakdown for a stay.
    Uses dynamic pricing: Cassandra overrides > weekend surcharge > seasonal > base.
    """
    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValueError("Check-out must be after check-in.")

    base = float(room.base_price_usd)
    overrides = _get_cassandra_overrides(room.id, check_in, check_out)

    nightly_prices = []
    for i in range(nights):
        day = check_in + datetime.timedelta(days=i)
        date_str = day.isoformat()

        if date_str in overrides:
            rate = overrides[date_str]
        else:
            rate = base
            # Seasonal multiplier
            mult = SEASONAL_MULTIPLIERS.get(day.month, 1.0)
            rate = round(rate * mult, 2)
            # Weekend surcharge (Fri=4, Sat=5)
            if day.weekday() in (4, 5):
                rate = round(rate * (1 + WEEKEND_SURCHARGE), 2)

        nightly_prices.append({'date': date_str, 'rate': rate})

    subtotal = round(sum(p['rate'] for p in nightly_prices), 2)
    avg_rate = round(subtotal / nights, 2)
    tax      = round(subtotal * TAX_RATE, 2)
    total    = round(subtotal + tax, 2)

    return {
        'nightly_rate':   avg_rate,
        'base_rate':      base,
        'nights':         nights,
        'nightly_prices': nightly_prices,
        'subtotal':       subtotal,
        'tax_rate':       TAX_RATE,
        'tax':            tax,
        'total':          total,
        'currency':       'usd',
    }


def price_in_cents(pricing: dict) -> int:
    """Convert total to integer cents for Stripe."""
    return int(pricing['total'] * 100)
