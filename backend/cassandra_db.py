"""
Cassandra database connection and schema for the hotel reservation system.
Supports both local Cassandra and DataStax Astra (cloud).
"""
import os
import uuid
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Configuration - use environment variables for flexibility
KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE', os.environ.get('ASTRA_DB_KEYSPACE', 'hotel'))

# Astra (cloud) - set these for production deployment
ASTRA_TOKEN = os.environ.get('ASTRA_DB_APPLICATION_TOKEN')
ASTRA_SECURE_BUNDLE = os.environ.get('ASTRA_DB_SECURE_BUNDLE_PATH')
if ASTRA_TOKEN and not ASTRA_SECURE_BUNDLE:
    # Fallback: look for bundle in backend directory (e.g. secure-connect-bundle.zip)
    _bundle_path = os.path.join(os.path.dirname(__file__), 'secure-connect-bundle.zip')
    if os.path.exists(_bundle_path):
        ASTRA_SECURE_BUNDLE = _bundle_path

# Local Cassandra - used when Astra vars are not set
CASSANDRA_HOSTS = os.environ.get('CASSANDRA_HOSTS', '127.0.0.1').split(',')
CASSANDRA_PORT = int(os.environ.get('CASSANDRA_PORT', 9042))

_session = None


def get_session():
    """Get or create a Cassandra session. Uses Astra if configured, else local Cassandra."""
    global _session
    if _session is None:
        if ASTRA_TOKEN and ASTRA_SECURE_BUNDLE:
            # DataStax Astra (cloud) connection
            cluster = Cluster(
                cloud={"secure_connect_bundle": ASTRA_SECURE_BUNDLE},
                auth_provider=PlainTextAuthProvider("token", ASTRA_TOKEN),
            )
        else:
            # Local Cassandra connection
            cluster = Cluster(
                contact_points=CASSANDRA_HOSTS,
                port=CASSANDRA_PORT,
            )
        _session = cluster.connect()
        init_schema()
    return _session


def init_schema():
    """Create keyspace and reservations table if they don't exist."""
    session = _session
    
    # Create keyspace with SimpleStrategy for single-node or small clusters
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
    """)
    
    session.set_keyspace(KEYSPACE)
    
    # Create reservations table
    # Partition key 'bucket' = 'all' allows fetching all reservations in one query
    # Clustering by (id) for uniqueness; we use id for updates/deletes
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {KEYSPACE}.reservations (
            bucket text,
            id uuid,
            first_name text,
            last_name text,
            birthday text,
            check_in_date text,
            check_out_date text,
            room_type text,
            extra_info text,
            status text,
            created_at text,
            PRIMARY KEY (bucket, id)
        )
    """)


def generate_id():
    """Generate a new UUID for reservation IDs."""
    return str(uuid.uuid4())


def create_reservation(data):
    """Insert a new reservation. Returns the reservation with generated id."""
    session = get_session()
    session.set_keyspace(KEYSPACE)
    
    reservation_id = generate_id()
    
    session.execute(
        """
        INSERT INTO reservations (
            bucket, id, first_name, last_name, birthday,
            check_in_date, check_out_date, room_type, extra_info, status, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            'all',
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


def get_all_reservations():
    """Fetch all reservations."""
    session = get_session()
    session.set_keyspace(KEYSPACE)
    
    rows = session.execute(
        "SELECT id, first_name, last_name, birthday, check_in_date, check_out_date, "
        "room_type, extra_info, status, created_at FROM reservations WHERE bucket = %s",
        ('all',)
    )
    
    reservations = []
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
    
    return reservations


def update_reservation_status(reservation_id, new_status):
    """Update a reservation's status. Returns True if updated, False if not found."""
    session = get_session()
    session.set_keyspace(KEYSPACE)
    
    try:
        # Check if row exists first (Cassandra UPDATE is upsert - would create phantom row)
        row = session.execute(
            "SELECT id FROM reservations WHERE bucket = %s AND id = %s",
            ('all', uuid.UUID(reservation_id))
        ).one()
        
        if row is None:
            return False
            
        session.execute(
            "UPDATE reservations SET status = %s WHERE bucket = %s AND id = %s",
            (new_status, 'all', uuid.UUID(reservation_id))
        )
        return True
    except Exception:
        return False


def delete_reservation(reservation_id):
    """Delete a reservation. Returns True if deleted, False if not found."""
    session = get_session()
    session.set_keyspace(KEYSPACE)
    
    try:
        # Check if exists first (Cassandra DELETE doesn't report affected rows)
        row = session.execute(
            "SELECT id FROM reservations WHERE bucket = %s AND id = %s",
            ('all', uuid.UUID(reservation_id))
        ).one()
        
        if row is None:
            return False
            
        session.execute(
            "DELETE FROM reservations WHERE bucket = %s AND id = %s",
            ('all', uuid.UUID(reservation_id))
        )
        return True
    except Exception:
        return False
