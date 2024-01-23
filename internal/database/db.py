from sqlalchemy import create_engine

from common import logging
from common.config import app


logger = logging.initialize_logging()

logger.info(logger, "Initializing database connection")

class DB:
    def __init__(self) -> None:
        self.conn_str = f"postgresql+psycopg2://{app.database_user}:{app.database_password}@{app.database_host}:{app.database_port}/{app.database_name}"
        if app.database_ssl_mode:
            self.conn_str += f"?sslmode={app.database_ssl_mode}"
        logger.info(logger, f"Database connection string: {self.conn_str}")

    def get_engine(self):
        engine = create_engine(self.conn_str)
        return engine
