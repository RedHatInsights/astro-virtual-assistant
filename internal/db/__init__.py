from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager

from common import logging
from common.config import app


logger = logging.initialize_logging()

# minconn and maxconn are arbitrary here, not sure what they should be
dbpool = ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    host=app.database_host,
    port=app.database_port,
    dbname=app.database_name,
    user=app.database_user,
    password=app.database_password,
)

logger.info("Database pool created")


@contextmanager
def db_cursor():
    if app.tracker_store_type == "InMemoryTrackerStore":
        logger.error("InMemoryTrackerStore can not be accessed")
        return
    
    conn = dbpool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Error occurred while accessing the database: " + str(e))
        raise
    finally:
        dbpool.putconn(conn)
