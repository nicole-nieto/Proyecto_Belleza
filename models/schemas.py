# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# ---------- USUARIO ----------
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: Optional[str] = "cliente"

class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    rol: Optional[str] = "cliente"

class UsuarioRead(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: str
    activo: bool

    class Config:
        from_attributes = True

# ---------- SPA ----------
class SpaCreate(BaseModel):
    nombre: str
    direccion: str
    zona: str
    horario: str

class SpaRead(BaseModel):
    id: int
    nombre: str
    direccion: str
    zona: str
    horario: str
    calificacion_promedio: float

    class Config:
        from_attributes = True

# ---------- SERVICIO ----------
class ServicioCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    duracion_ref: Optional[str] = None
    precio_ref: Optional[float] = None

class ServicioRead(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    duracion_ref: Optional[str] = None
    precio_ref: Optional[float] = None

    class Config:
        from_attributes = True

# ---------- MATERIAL ----------
class MaterialCreate(BaseModel):
    nombre: str
    tipo: str

class MaterialRead(BaseModel):
    id: int
    nombre: str
    tipo: str

    class Config:
        from_attributes = True

# ---------- RESEÑA ----------
class ResenaCreate(BaseModel):
    calificacion: int
    comentario: str
    fecha_creacion: date
    spa_id: int
    usuario_id: int

class ResenaRead(BaseModel):
    id: int
    calificacion: int
    comentario: str
    fecha_creacion: date
    spa_id: int
    usuario_id: int

    class Config:
        from_attributes = True
