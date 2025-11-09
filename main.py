from fastapi import FastAPI
from core.db import create_db_and_tables
from routers import spa_router, servicio_router, material_router, usuario_router, resena_router, auth_router, reporte_router

app = FastAPI(title="Proyecto Belleza - API")

# Crear tablas automáticamente al iniciar
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Incluir rutas
app.include_router(spa_router.router)
app.include_router(servicio_router.router)
app.include_router(material_router.router)
app.include_router(usuario_router.router)
app.include_router(resena_router.router)
app.include_router(auth_router.router)
app.include_router(reporte_router.router)

@app.get("/")
def home():
    return {"mensaje": "Bienvenida a la API de Spas del barrio laguna-Fontibon 💅"}
