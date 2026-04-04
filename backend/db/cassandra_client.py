"""
Cassandra database connection and schema for the hotel reservation system.
Supports both local Cassandra and DataStax Astra (cloud).

SCHEMA MIGRATION NOTE:
  The old schema used `bucket='all'` as the partition key, which creates a single
  hot partition that won't scale. The new schema partitions by `check_in_month`
  (format: 'YYYY-MM'), distributing records across monthly partitions.

  If you have an existing `reservations` table with the old schema, drop it first:
    DROP TABLE <keyspace>.reservations;
  The new table will be created automatically on next server start.
"""
import os
import uuid
import datetime

# cassandra-driver doesn't yet have a wheel for Python 3.14.
# Imports are deferred to get_session() so the app and seed script
# can start without it installed locally. On Render (Python 3.11)
# the package installs fine and all Cassandra functionality works.
try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    from cassandra.concurrent import execute_concurrent_with_args
    _CASSANDRA_AVAILABLE = True
except ImportError:
    _CASSANDRA_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KEYSPACE = (
    os.environ.get('CASSANDRA_KEYSPACE') or
    os.environ.get('ASTRA_DB_KEYSPACE') or
    ('default_keyspace' if os.environ.get('ASTRA_DB_APPLICATION_TOKEN') else 'hotel')
)

ASTRA_TOKEN = os.environ.get('ASTRA_DB_APPLICATION_TOKEN')
ASTRA_SECURE_BUNDLE = os.environ.get('ASTRA_DB_SECURE_BUNDLE_PATH')
if ASTRA_TOKEN and not ASTRA_SECURE_BUNDLE:
    _bundle_path = os.path.join(os.path.dirname(__file__), '..', 'secure-connect-bundle.zip')
    if os.path.exists(_bundle_path):
        ASTRA_SECURE_BUNDLE = _bundle_path

CASSANDRA_HOSTS = os.environ.get('CASSANDRA_HOSTS', '127.0.0.1').split(',')
CASSANDRA_PORT = int(os.environ.get('CASSANDRA_PORT', 9042))

_session = None


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_session():
    """Get or create a Cassandra session. Uses Astra if configured, else local."""
    if not _CASSANDRA_AVAILABLE:
        raise RuntimeError(
            "cassandra-driver is not installed. "
            "It will be available on Render (Python 3.11). "
            "Cassandra features are disabled in this local environment."
        )
    global _session
    if _session is None:
        if ASTRA_TOKEN and ASTRA_SECURE_BUNDLE:
            cluster = Cluster(
                cloud={"secure_connect_bundle": ASTRA_SECURE_BUNDLE},
                auth_provider=PlainTextAuthProvider("token", ASTRA_TOKEN),
            )
        else:
            cluster = Cluster(
                contact_points=CASSANDRA_HOSTS,
                port=CASSANDRA_PORT,
            )
        _session = cluster.connect()
        init_schema()
    return _session


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_schema():
    """Create keyspace and tables if they don't exist. Auto-migrates old schema."""
    session = _session

    if not (ASTRA_TOKEN and ASTRA_SECURE_BUNDLE):
        try:
            session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
            """)
        except Exception:
            pass

    session.set_keyspace(KEYSPACE)

    # Auto-migrate: if the old bucket-partitioned table exists, drop it so the
    # new check_in_month schema is created cleanly below.
    if _has_old_schema(session):
        print("[cassandra] Detected old bucket='all' schema — dropping reservations table for migration.")
        session.execute(f"DROP TABLE IF EXISTS {KEYSPACE}.reservations")

    # Reservations table — partitioned by check_in_month ('YYYY-MM') so records
    # are spread across monthly partitions instead of piling into a single 'all' bucket.
    # To query all reservations we fetch a range of months in parallel (see get_all_reservations).
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {KEYSPACE}.reservations (
            check_in_month text,
            id             uuid,
            first_name     text,
            last_name      text,
            birthday       text,
            check_in_date  text,
            check_out_date text,
            room_type      text,
            extra_info     text,
            status         text,
            created_at     text,
            PRIMARY KEY (check_in_month, id)
        ) WITH CLUSTERING ORDER BY (id ASC)
    """)

    # Room availability calendar — partitioned by (room_id, year_month).
    # One row per room per night. missing row = fully available.
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {KEYSPACE}.room_availability (
            room_id         text,
            year_month      text,
            stay_date       text,
            available_units smallint,
            price_override  decimal,
            PRIMARY KEY ((room_id, year_month), stay_date)
        ) WITH CLUSTERING ORDER BY (stay_date ASC)
    """)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_old_schema(session) -> bool:
    """Return True if the reservations table still uses the old bucket partition key."""
    try:
        row = session.execute(
            "SELECT column_name FROM system_schema.columns "
            "WHERE keyspace_name = %s AND table_name = 'reservations' AND column_name = 'bucket'",
            (KEYSPACE,)
        ).one()
        return row is not None
    except Exception:
        return False


def _month_range(months_back: int = 3, months_forward: int = 12) -> list[str]:
    """Return a list of 'YYYY-MM' strings covering a rolling window."""
    today = datetime.date.today()
    months = []
    for delta in range(-months_back, months_forward + 1):
        year = today.year + (today.month - 1 + delta) // 12
        month = (today.month - 1 + delta) % 12 + 1
        months.append(f"{year:04d}-{month:02d}")
    return months


def _check_in_month(check_in_date: str) -> str:
    """Extract 'YYYY-MM' from a 'YYYY-MM-DD' date string."""
    return check_in_date[:7]


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_reservation(data: dict) -> dict:
    """Insert a new reservation. Returns the reservation dict with generated id."""
    session = get_session()
    session.set_keyspace(KEYSPACE)

    reservation_id = str(uuid.uuid4())
    month = _check_in_month(data['check_in_date'])

    session.execute(
        """
        INSERT INTO reservations (
            check_in_month, id, first_name, last_name, birthday,
            check_in_date, check_out_date, room_type, extra_info, status, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            month,
            uuid.UUID(reservation_id),
            data.get('first_name'),
            data.get('last_name'),
            data.get('birthday'),
            data.get('check_in_date'),
            data.get('check_out_date'),
            data.get('room_type'),
            data.get('extra_info'),
            data.get('status'),
            data.get('created_at'),
        )
    )

    return {**data, 'id': reservation_id}


def get_all_reservations() -> list[dict]:
    """
    Fetch all reservations across a rolling window of monthly partitions.
    Queries each month partition individually (Cassandra best practice for
    partition-key-only queries) and merges the results in Python.
    """
    session = get_session()
    session.set_keyspace(KEYSPACE)

    stmt = session.prepare(
        "SELECT id, first_name, last_name, birthday, check_in_date, check_out_date, "
        "room_type, extra_info, status, created_at "
        "FROM reservations WHERE check_in_month = ?"
    )

    months = _month_range()
    params = [(m,) for m in months]

    results = execute_concurrent_with_args(session, stmt, params, raise_on_first_error=False)

    reservations = []
    for (success, rows) in results:
        if not success:
            continue
        for row in rows:
            reservations.append({
                'id': str(row.id),
                'first_name': row.first_name,
                'last_name': row.last_name,
                'birthday': row.birthday,
                'check_in_date': row.check_in_date,
                'check_out_date': row.check_out_date,
                'room_type': row.room_type,
                'extra_info': row.extra_info,
                'status': row.status,
                'created_at': row.created_at,
            })

    # Sort by check_in_date descending so newest appear first
    reservations.sort(key=lambda r: r.get('check_in_date', ''), reverse=True)
    return reservations


def update_reservation_status(reservation_id: str, new_status: str, check_in_date: str = None) -> bool:
    """
    Update a reservation's status. Returns True if updated, False if not found.

    If check_in_date is provided, only that month partition is searched.
    Otherwise all partitions in the rolling window are searched (slower).
    """
    session = get_session()
    session.set_keyspace(KEYSPACE)

    try:
        rid = uuid.UUID(reservation_id)
    except ValueError:
        return False

    months = [_check_in_month(check_in_date)] if check_in_date else _month_range()

    for month in months:
        try:
            row = session.execute(
                "SELECT id FROM reservations WHERE check_in_month = %s AND id = %s",
                (month, rid)
            ).one()
            if row is not None:
                session.execute(
                    "UPDATE reservations SET status = %s WHERE check_in_month = %s AND id = %s",
                    (new_status, month, rid)
                )
                return True
        except Exception:
            continue

    return False


def delete_reservation(reservation_id: str, check_in_date: str = None) -> bool:
    """
    Delete a reservation. Returns True if deleted, False if not found.

    If check_in_date is provided, only that month partition is searched.
    Otherwise all partitions in the rolling window are searched (slower).
    """
    session = get_session()
    session.set_keyspace(KEYSPACE)

    try:
        rid = uuid.UUID(reservation_id)
    except ValueError:
        return False

    months = [_check_in_month(check_in_date)] if check_in_date else _month_range()

    for month in months:
        try:
            row = session.execute(
                "SELECT id FROM reservations WHERE check_in_month = %s AND id = %s",
                (month, rid)
            ).one()
            if row is not None:
                session.execute(
                    "DELETE FROM reservations WHERE check_in_month = %s AND id = %s",
                    (month, rid)
                )
                return True
        except Exception:
            continue

    return False


# ---------------------------------------------------------------------------
# Room availability (Phase 3)
# ---------------------------------------------------------------------------

def get_room_availability_month(room_id: str, year_month: str) -> list[dict]:
    """Return all availability rows for a room in a given month ('YYYY-MM')."""
    session = get_session()
    session.set_keyspace(KEYSPACE)
    rows = session.execute(
        "SELECT stay_date, available_units, price_override "
        "FROM room_availability WHERE room_id = %s AND year_month = %s",
        (room_id, year_month)
    )
    return [
        {
            'stay_date':       str(row.stay_date),
            'available_units': row.available_units,
            'price_override':  float(row.price_override) if row.price_override else None,
        }
        for row in rows
    ]


def decrement_room_availability(room_id: str, check_in, check_out, total_units: int):
    """
    Reduce available_units by 1 for every night in [check_in, check_out).
    If no row exists for a night, creates one with total_units - 1.
    check_in / check_out are datetime.date objects.
    """
    import datetime as dt
    session = get_session()
    session.set_keyspace(KEYSPACE)
    current = check_in
    while current < check_out:
        ym       = current.strftime('%Y-%m')
        date_str = current.isoformat()
        row = session.execute(
            "SELECT available_units FROM room_availability "
            "WHERE room_id = %s AND year_month = %s AND stay_date = %s",
            (room_id, ym, date_str)
        ).one()
        new_units = max((row.available_units - 1) if row is not None else (total_units - 1), 0)
        session.execute(
            "INSERT INTO room_availability (room_id, year_month, stay_date, available_units) "
            "VALUES (%s, %s, %s, %s)",
            (room_id, ym, date_str, new_units)
        )
        current += dt.timedelta(days=1)


def increment_room_availability(room_id: str, check_in, check_out, total_units: int):
    """Restore available_units by 1 per night — used on booking cancellation."""
    import datetime as dt
    session = get_session()
    session.set_keyspace(KEYSPACE)
    current = check_in
    while current < check_out:
        ym       = current.strftime('%Y-%m')
        date_str = current.isoformat()
        row = session.execute(
            "SELECT available_units FROM room_availability "
            "WHERE room_id = %s AND year_month = %s AND stay_date = %s",
            (room_id, ym, date_str)
        ).one()
        new_units = min((row.available_units + 1) if row is not None else total_units, total_units)
        session.execute(
            "INSERT INTO room_availability (room_id, year_month, stay_date, available_units) "
            "VALUES (%s, %s, %s, %s)",
            (room_id, ym, date_str, new_units)
        )
        current += dt.timedelta(days=1)
