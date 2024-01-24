from sqlalchemy import create_engine

from common import logging
from common.config import app


logger = logging.initialize_logging()

logger.info("Initializing database connection")


class DB:
    def __init__(self) -> None:
        self.conn_str = f"postgresql+psycopg2://{app.database_user}:{app.database_password}@{app.database_host}:{app.database_port}/{app.database_name}"
        if app.database_ssl_mode:
            self.conn_str += f"?sslmode={app.database_ssl_mode}"

        self.conn_args = None
        if app.database_ca_path:
            self.conn_args = {"sslrootcert": app.database_ca_path}

    def get_engine(self):
        engine = create_engine(self.conn_str, connect_args=self.conn_args)
        return engine
