☻ Beauty Nails — Plataforma Web de Spas de Uñas

FastAPI · SQLModel · PostgreSQL · Render · Python

📖 Descripción

Este proyecto desarrolla una plataforma web que permite a las personas —principalmente mujeres— encontrar spas de uñas en el barrio Laguna (Fontibón, Bogotá) con información clara sobre:

Ubicación

Servicios

Materiales utilizados

Precios

Calidad y calificación

El objetivo es facilitar el acceso a opciones de cuidado estético confiables, seguras y accesibles.
El proyecto integra datos recolectados desde redes sociales, directorios locales y un dataset propio, con un backend robusto y un frontend simple y amigable.



✨ Características Principales

🏠 Interfaz Web Moderna: HTML, CSS y templates Jinja2

📱 API REST Completa: CRUD para modelos

⭐ Sistema de Calificaciones: Usuarios dejan reseñas reales

🖼️ Gestión de Imágenes: Archivos guardados en PostgreSQL

🔐 Autenticación JWT: Roles: usuario, admin_spa, admin_principal



📘 Diagrama de Clases

<img width="921" height="899" alt="image" src="https://github.com/user-attachments/assets/071b17aa-9cda-4cc6-a8e6-609ffd1fffc5" />



🛣️ ENDPOINTS

| Método     | Endpoint                  | Descripción            |
| ---------- | ------------------------- | ---------------------- |
| **POST**   | `/spas/`                  | Crear spa              |
| **GET**    | `/spas/`                  | Listar spas            |
| **GET**    | `/spas/{spa_id}`          | Obtener spa            |
| **PATCH**  | `/spas/{spa_id}`          | Actualizar spa         |
| **DELETE** | `/spas/{spa_id}`          | Desactivar spa         |
| **GET**    | `/spas/buscar/`           | Buscar spa por filtros |
| **PATCH**  | `/spas/{spa_id}/restore`  | Restaurar spa          |
| **POST**   | `/spas/{spa_id}/imagenes` | Subir imagen de spa    |

| Método     | Endpoint                                     | Descripción               |
| ---------- | -------------------------------------------- | ------------------------- |
| **POST**   | `/materiales/`                               | Crear material            |
| **GET**    | `/materiales/`                               | Listar materiales         |
| **POST**   | `/materiales/asociar/{spa_id}/{material_id}` | Asociar material a spa    |
| **PATCH**  | `/materiales/{material_id}`                  | Actualizar material       |
| **DELETE** | `/materiales/{material_id}`                  | Eliminar material         |
| **GET**    | `/materiales/por_spa/{spa_id}`               | Listar materiales por spa |


| Método     | Endpoint                                    | Descripción                                |
| ---------- | ------------------------------------------- | ------------------------------------------ |
| **POST**   | `/servicios/`                               | Crear servicio base (solo admin_principal) |
| **GET**    | `/servicios/`                               | Listar servicios globales                  |
| **POST**   | `/servicios/asociar/{spa_id}/{servicio_id}` | Asociar servicio a spa                     |
| **GET**    | `/servicios/por_spa/{spa_id}`               | Listar servicios de un spa                 |
| **PATCH**  | `/servicios/{servicio_id}`                  | Actualizar servicio base                   |
| **DELETE** | `/servicios/{servicio_id}`                  | Eliminar servicio                          |


| Método   | Endpoint            | Descripción                        |
| -------- | ------------------- | ---------------------------------- |
| **POST** | `/auth/register`    | Registrar usuario (rol: usuario)   |
| **POST** | `/auth/login`       | Login con JWT                      |
| **POST** | `/auth/setup_admin` | Crear admin principal (solo 1 vez) |

| Método    | Endpoint                            | Descripción                      |
| --------- | ----------------------------------- | -------------------------------- |
| **GET**   | `/usuarios/perfil`                  | Ver perfil (solo usuario normal) |
| **POST**  | `/usuarios/crear_admin_spa`         | Crear admin de spa               |
| **GET**   | `/usuarios/`                        | Listar usuarios                  |
| **GET**   | `/usuarios/{usuario_id}`            | Obtener usuario por ID           |
| **PATCH** | `/usuarios/desactivar/{usuario_id}` | Desactivar usuario               |
| **PATCH** | `/usuarios/activar/{usuario_id}`    | Activar usuario                  |

| Método     | Endpoint                    | Descripción            |
| ---------- | --------------------------- | ---------------------- |
| **POST**   | `/resenas/`                 | Crear reseña           |
| **GET**    | `/resenas/por_spa/{spa_id}` | Listar reseñas por spa |
| **GET**    | `/resenas/mias`             | Listar mis reseñas     |
| **PATCH**  | `/resenas/{resena_id}`      | Actualizar reseña      |
| **DELETE** | `/resenas/{resena_id}`      | Eliminación lógica     |
| **GET**    | `/resenas/todas_admin`      | Listar todas (admins)  |


| Método  | Endpoint                     | Descripción                        |
| ------- | ---------------------------- | ---------------------------------- |
| **GET** | `/reportes/resenas_por_spa`  | Total de reseñas por spa           |
| **GET** | `/reportes/promedio_por_spa` | Promedio de calificaciones por spa |


📁 Estructura del Proyecto
PROYECTO_BELLEZA/
├── core/                  <-- Lógica central (auth, config, db, utils)
│   ├── auth.py
│   ├── config.py
│   ├── db.py
│   └── utils.py
├── models/                <-- Modelos de datos y esquemas Pydantic
│   ├── models.py
│   └── schemas.py
├── routers/               <-- Controladores de Endpoints (API)
│   ├── auth_router.py
│   ├── spa_router.py
│   ├── servicio_router.py
│   ├── material_router.py
│   ├── resena_router.py
│   ├── usuario_router.py
│   └── reporte_router.py
├── static/                <-- Recursos estáticos del Frontend
│   ├── css/
│   ├── img/
│   └── js/
├── templates/             <-- Archivos HTML (Templates Jinja)
├── main.py                <-- Punto de entrada de la aplicación
├── requirements.txt
├── .env
└── README.md



☁️ Despliegue
                ┌────────────────────────────────────────┐
                │             CLIENTE (WEB)              │
                │      HTML, CSS, JS (Fetch API)         │
                └────────────────────────────────────────┘
                                      │
                                      ▼
                           Peticiones HTTPS
                                      │
                                      ▼
              ┌──────────────────────────────────────────┐
              │               FASTAPI APP                │
              │                (main.py)                 │
              ├──────────────────────────────────────────┤
              │ Routers: auth, spas, servicios, etc      │
              └──────────────────────────────────────────┘
                                      │
                                      ▼
              ┌──────────────────────────────────────────┐
              │                  CORE                    │
              │   db.py – conexión PostgreSQL            │
              │   auth.py – JWT, Hash, roles             │
              └──────────────────────────────────────────┘
                                      │
                                      ▼
              ┌──────────────────────────────────────────┐
              │                BASE DE DATOS             │
              │         PostgreSQL (Render.com)          │
              └──────────────────────────────────────────┘




🛠️ Stack Tecnológico
🖥️ Backend

 - FastAPI — Framework principal
  
 - SQLModel + SQLAlchemy 2.0 — Modelado de datos
  
 - Pydantic v2 — Validación
  
 - Passlib + Bcrypt — Hashing de contraseñas
  
 - Python-JOSE (JWT) — Autenticación
  
 - psycopg / psycopg2-binary — Conexión PostgreSQL
  
 - python-multipart — Subida de archivos

🎨 Frontend

 - Jinja2 — Templates
  
 - HTML + CSS + JavaScript
  
 - 🗄️ Base de Datos

PostgreSQL (Render) — Producción
  
 - ☁️ Servicios / Despliegue
  
 - Render.com — Hosting backend
  
 - Render PostgreSQL — Base de datos
  
 - .env + pydantic-settings — Configuración segura
