# core/db.py
import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# URL de la base de datos PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL")

# Crear el motor de conexión
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Crea todas las tablas si no existen."""
    from models.models import Usuario, Spa, Servicio, Material, Resena
    SQLModel.metadata.create_all(engine)

def get_session():
    """Devuelve una sesión de base de datos para usar con FastAPI."""
    with Session(engine) as session:
        yield session
