from sqlmodel import SQLModel, Session, create_engine, select
from models.models import Usuario, Spa, Servicio, Material, Resena, SpaServicio, SpaMaterial
import sqlite3

# -------------------------
# 🔗 Conexiones
# -------------------------
sqlite_url = "sqlite:///belleza.db"
pg_url = "postgresql+psycopg2://postgres:admin123@localhost:5432/belleza"

sqlite_engine = create_engine(sqlite_url)
pg_engine = create_engine(pg_url)

# -------------------------
# 🏗️ Crear tablas en PostgreSQL (si no existen)
# -------------------------
print("⏳ Creando tablas en PostgreSQL (si no existen)...")
SQLModel.metadata.create_all(pg_engine)
print("✅ Tablas listas.")

# -------------------------
# 🚚 Migrar datos
# -------------------------
with Session(sqlite_engine) as sqlite_s, Session(pg_engine) as pg_s:
    print("⏳ Migrando datos desde SQLite a PostgreSQL...")

    # Usuarios
    usuarios = sqlite_s.exec(select(Usuario)).all()
    for u in usuarios:
        pg_s.add(Usuario(**u.dict()))

    # Spas
    spas = sqlite_s.exec(select(Spa)).all()
    for s in spas:
        pg_s.add(Spa(**s.dict()))

    # Servicios
    servicios = sqlite_s.exec(select(Servicio)).all()
    for serv in servicios:
        pg_s.add(Servicio(**serv.dict()))

    # Materiales
    materiales = sqlite_s.exec(select(Material)).all()
    for m in materiales:
        pg_s.add(Material(**m.dict()))

    # Reseñas
    resenas = sqlite_s.exec(select(Resena)).all()
    for r in resenas:
        pg_s.add(Resena(**r.dict()))

    # SpaServicio (tabla 'spaservicio' en SQLite)
    result_spaserv = sqlite_s.exec(select(SpaServicio)).all()
    for ss in result_spaserv:
        pg_s.add(SpaServicio(**ss.dict()))

    # SpaMaterial (tabla 'spamaterial' en SQLite)
    result_spamat = sqlite_s.exec(select(SpaMaterial)).all()
    for sm in result_spamat:
        pg_s.add(SpaMaterial(**sm.dict()))

    pg_s.commit()
    print("✅ Migración completada con éxito.")
