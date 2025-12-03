from core.db import create_db_and_tables
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import router as auth_router
from routers.spa_router import router as spa_router
from routers.servicio_router import router as servicio_router
from routers.material_router import router as material_router
from routers.usuario_router import router as usuario_router
from routers.reporte_router import router as reporte_router
from routers.resena_router import router as resena_router

app = FastAPI()

# CORS CORRECTO
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STATIC
app.mount("/static", StaticFiles(directory="static"), name="static")

# TEMPLATES
templates = Jinja2Templates(directory="templates")

@app.get("/spa_detalle")
def spa_detalle(request: Request):
    return templates.TemplateResponse("spa_detalle.html", {"request": request})

# ROUTERS
app.include_router(auth_router)
app.include_router(spa_router)
app.include_router(servicio_router)
app.include_router(material_router)
app.include_router(usuario_router)
app.include_router(reporte_router)
app.include_router(resena_router)

# startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# PÁGINAS FRONTEND
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/spas", response_class=HTMLResponse)
def spa_page(request: Request):
    return templates.TemplateResponse("spas.html", {"request": request})

@app.get("/spa/{spa_id}", response_class=HTMLResponse)
def spa_detail(request: Request, spa_id: int):
    return templates.TemplateResponse("spa_detail.html", {"request": request, "spa_id": spa_id})

@app.get("/servicios", response_class=HTMLResponse)
def servicios_page(request: Request):
    return templates.TemplateResponse("servicios.html", {"request": request})

@app.get("/materiales", response_class=HTMLResponse)
def materiales_page(request: Request):
    return templates.TemplateResponse("materiales.html", {"request": request})

@app.get("/usuarios", response_class=HTMLResponse)
def usuarios_page(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})

@app.get("/reportes", response_class=HTMLResponse)
def reportes_page(request: Request):
    return templates.TemplateResponse("reportes.html", {"request": request})

@app.get("/resenas", response_class=HTMLResponse)
def resenas_page(request: Request):
    return templates.TemplateResponse("resenas.html", {"request": request})
