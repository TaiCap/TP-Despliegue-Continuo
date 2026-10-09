import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("MYSQL_USER", "docker_user")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "docker_password")
DB_HOST = os.getenv("MYSQL_HOST", "mysql")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DATABASE", "docker_tp")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# En Aiven la conexión tiene que ir encriptada (SSL).
# Lo activamos solo si la variable MYSQL_SSL vale "true",
# así en mi PC con Docker sigue funcionando igual.
USE_SSL = os.getenv("MYSQL_SSL", "false").lower() == "true"

connect_args = {}
if USE_SSL:
    connect_args = {"ssl": {"check_hostname": False}}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
