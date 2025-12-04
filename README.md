Beauty Nails

FastAPI SQLModel Supabase Python Render Postgresql

📖 Descripción
El presente proyecto busca modelar y desarrollar una plataforma web que permita a las personas, principalmente mujeres, encontrar spas de uñas en el barrio laguna de la localidad de Fontibón de la ciudad de Bogotá con información clara sobre ubicación, servicios, materiales utilizados, precios, calidad y reconocimiento. El propósito no se limita únicamente a la creación de una aplicación tecnológica, sino a generar un impacto positivo en los usuarios al facilitarles el acceso a opciones de cuidado estético que contribuyan a sentirse más bonitas, seguras y cuidadas. Para ello, se emplearán fuentes abiertas, datos recolectados de redes sociales y directorios locales, complementados con un dataset propio. El proyecto se apoyará en modelos de datos estructurados y en un backend que asegure la gestión de información, además de un frontend que permita la interacción intuitiva y amigable con el usuario final. 

✨ Características Principales
🏠 Interfaz Web Moderna: Templates con CSS y navegación intuitiva
📱 API RESTful Completa: Endpoints para todas las operaciones CRUD
🖼️ Gestión de Imágenes: Subida y almacenamiento en postgres

Diagrama de clases

<img width="921" height="899" alt="image" src="https://github.com/user-attachments/assets/071b17aa-9cda-4cc6-a8e6-609ffd1fffc5" />

ENDPOINTS

/spas
│
├── POST /spas/                     → Crear spa
├── GET  /spas/                     → Listar spas
├── GET  /spas/{spa_id}             → Obtener spa
├── PATCH /spas/{spa_id}            → Actualizar spa
├── DELETE /spas/{spa_id}           → Desactivar spa
├── GET /spas/buscar/               → Buscar spa por filtros
├── PATCH /spas/{spa_id}/restore    → Restaurar spa
└── POST /spas/{spa_id}/imagenes    → Subir imagen de spa

/materiales
 ├── POST / → crear material
 ├── GET / → listar materiales
 ├── POST /asociar/{spa_id}/{material_id} → asociar material a spa
 ├── PATCH /{material_id} → actualizar material
 ├── DELETE /{material_id} → eliminar material
 └── GET /por_spa/{spa_id} → listar materiales por spa
 
/servicios
 ├── POST / → crear servicio base (solo admin_principal)
 ├── GET / → listar servicios globales
 ├── POST /asociar/{spa_id}/{servicio_id} → asociar servicio a un spa
 ├── GET /por_spa/{spa_id} → listar servicios de un spa
 ├── PATCH /{servicio_id} → actualizar servicio base
 └── DELETE /{servicio_id} → eliminar servicio definitivamente
 
/auth
 ├── POST /register → registrar usuario (rol: usuario)
 ├── POST /login → iniciar sesión (JWT)
 └── POST /setup_admin → crear admin principal inicial (solo 1 vez)
 
/usuarios
 ├── GET    /perfil                         → ver perfil (solo usuario normal)
 ├── POST   /crear_admin_spa                → crear admin de spa (admin_principal)
 ├── GET    /                                → listar usuarios (admin_principal)
 ├── GET    /{usuario_id}                   → obtener usuario por ID
 ├── PATCH  /desactivar/{usuario_id}        → desactivar usuario (admin_principal)
 └── PATCH  /activar/{usuario_id}           → activar usuario (admin_principal)
 
/resenas
 ├── POST   /                                 → crear reseña (solo usuario)
 ├── GET    /por_spa/{spa_id}                 → listar reseñas por spa
 ├── GET    /mias                              → listar mis reseñas
 ├── PATCH  /{resena_id}                      → actualizar reseña
 ├── DELETE /{resena_id}                      → eliminar reseña (lógico)
 └── GET    /todas_admin                      → listar todas (admin / admin_principal)
 
/reportes
 ├── GET  /resenas_por_spa        → cantidad de reseñas agrupadas por spa
 └── GET  /promedio_por_spa       → promedio de calificaciones por spa

ESTRUCTURA DEL PROYECTO
PROYECTO_BELLEZA/
├── 📂 core/                     # Núcleo del sistema
│   ├── auth.py                 # Lógica de autenticación (JWT, hashing)
│   ├── config.py               # Configuraciones globales
│   ├── db.py                   # Conexión y sesión con la base de datos
│   └── utils.py                # Funciones de utilidad generales
│
├── 📂 models/                   # Modelos de datos
│   ├── models.py               # Modelos SQLModel 
│   └── schemas.py              # Esquemas Pydantic (Request/Response)
│
├── 📂 routers/                  # endpoints de la API
├── 📂 static/                   # Archivos estáticos del frontend
│   ├── 📂 css/
│   │   └── style.css           # Estilos globales de la app
│   ├── 📂 img/                 # Imágenes (spas, logos, etc)
│   └── 📂 js/                  # Lógica frontend
├── 📂 templates/               # Templates HTML (Jinja2)
├── 📄 main.py                  # Punto principal de la aplicación FastAPI
├── 📄 requirements.txt         # Dependencias del proyecto
├── 📄 .env                     # Variables de entorno (DB, JWT_SECRET)
└── 📄 README.md                # Documentación principal del proyecto



Despliegue
                ┌────────────────────────────────────────┐
                │             CLIENTE (WEB)              │
                │  Navegador: HTML, CSS, JS (Fetch API)  │
                └────────────────────────────────────────┘
                                      │
                              Peticiones HTTPS
                                      │
                                      ▼
              ┌──────────────────────────────────────────┐
              │               FASTAPI APP                │
              │                (main.py)                 │
              ├──────────────────────────────────────────┤
              │ Routers:                                 │
              │   - auth_router                          │
              │   - spa_router                           │
              │   - servicio_router                      │
              │   - material_router                      │
              │   - resena_router                        │
              │   - reporte_router                       │
              │   - usuario_router                       │
              └──────────────────────────────────────────┘
                                      │
                                      ▼
              ┌──────────────────────────────────────────┐
              │                  CORE                    │
              │  - db.py → conexión a base de datos      │
              │  - auth.py → JWT, Hash, permisos         │
              │  - utils.py                              │
              └──────────────────────────────────────────┘
                                      │
                                      ▼
              ┌──────────────────────────────────────────┐
              │                BASE DE DATOS             │
              │        SQLModel / SQLite / PostgreSQL    │
              │    Tablas: Usuario, Spa, Servicio, etc.  │
              └──────────────────────────────────────────┘



🛠️ Stack Tecnológico 
🖥️ Backend
    •	FastAPI — Framework principal para construir la API.
    •	SQLModel + SQLAlchemy 2.0 — ORM y modelo de datos con tipado.
    •	Pydantic v2 — Validación y serialización de datos.
    •	Passlib + Bcrypt — Hashing seguro de contraseñas.
    •	Python-JOSE (JWT) — Autenticación basada en tokens.
    •	psycopg2 / psycopg — Conexión con PostgreSQL.
    •	python-multipart — Manejo de formularios y subida de archivos.
🎨 Frontend
    •	Jinja2 — Sistema de templates.
    •	HTML + CSS + JS — Construcción de interfaces.
🗄️ Base de Datos
    •	PostgreSQL (Render) — Motor de base de datos en producción.
☁️ Servicios / Despliegue
    •	Render.com — Hosting del backend (FastAPI) + PostgreSQL.
    •	.env + pydantic-settings — Gestión de configuración segura


