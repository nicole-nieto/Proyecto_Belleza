import os
from sqlmodel import SQLModel, create_engine, Session

# Usa la URL externa de Render (para conexiones desde tu máquina local)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://belleza_db_user:ykTYfCULlkgFhGdNuQrQMuuZ9WxgDoyu@dpg-d48ct7jipnbc73de1lgg-a.oregon-postgres.render.com/belleza_db"
)

# Conecta al motor de base de datos PostgreSQL
engine = create_engine(DATABASE_URL, echo=True)

# Sesión para manejar las transacciones
def get_session():
    with Session(engine) as session:
        yield session

# Crea las tablas a partir de los modelos
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
