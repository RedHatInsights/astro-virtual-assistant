from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.config import app

class DB:
    def __init__(self) -> None:
        self.conn_str = f"postgresql+psycopg2://{app.database_user}:{app.database_password}@{app.database_host}:{app.database_port}/{app.database_name}"
        if app.database_ssl_mode:
            self.conn_str += f"?sslmode={app.database_ssl_mode}"

    def get_engine(self):
        engine = create_engine(self.conn_str)
        return engine
