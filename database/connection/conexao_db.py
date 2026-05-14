import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pasta_auth = Path(__file__).parent
load_dotenv(pasta_auth / ".env")


class ConexaoDB:

    def __init__(self):
        self._engine = None
        self._session = None

    def conectar_banco(self, usar_banco: bool = True):
        if self._session:
            self._session.close()
        try:
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            database = os.getenv("DB_NAME") if usar_banco else ""

            db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

            self._engine = create_engine(db_url)
            self._session = sessionmaker(bind=self._engine)()
            return self._session

        except Exception:
            return None

    def desconectar_banco(self, session) -> None:
        if session:
            session.close()
