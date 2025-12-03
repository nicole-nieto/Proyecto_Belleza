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
    rol: Optional[str] = "usuario"

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
    horario: Optional[str] = None
    calificacion_promedio: float
    activo: bool                   # ✔ NECESARIO
    ultima_actualizacion: Optional[date] = None


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
    class Config:
        orm_mode = True

class MaterialRead(BaseModel):
    id: int
    nombre: str
    tipo: str

    class Config:
        from_attributes = True

class MaterialUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None


# ---------- RESEÑA ----------
class ResenaCreate(BaseModel):
    calificacion: int
    comentario: str
    spa_id: int


class ResenaRead(BaseModel):
    id: int
    calificacion: int
    comentario: str
    fecha_creacion: date
    spa_id: int
    spa_nombre: Optional[str] = None        # <-- agregado para mostrar nombre del spa en frontend
    usuario_id: int
    usuario_nombre: Optional[str] = None    # <-- opcional, útil para vistas admin

    class Config:
        orm_mode = True

# ---------- SPA UPDATE ----------
class SpaUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    zona: Optional[str] = None
    horario: Optional[str] = None   

    class Config:
        orm_mode = True


class SpaServicioRead(BaseModel):
    id: int
    servicio_id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    duracion: Optional[str] = None

    class Config:
        from_attributes = True


class SpaMaterialRead(BaseModel):
    id: int
    nombre: str
    tipo: Optional[str]

    class Config:
        from_attributes = True


class ResenaSimpleRead(BaseModel):
    id: int
    calificacion: int
    comentario: str
    fecha_creacion: date
    usuario_id: int
    usuario_nombre: Optional[str]

    class Config:
        from_attributes = True


class SpaDetalleRead(BaseModel):
    id: int
    nombre: str
    direccion: str
    zona: str
    horario: Optional[str]
    calificacion_promedio: float
    ultima_actualizacion: Optional[date]

    servicios: list[SpaServicioRead]
    materiales: list[SpaMaterialRead]
    resenas: list[ResenaSimpleRead]

    class Config:
        from_attributes = True
from pydantic import BaseModel

class AsociarServicio(BaseModel):
    precio: float
    duracion: str
