# Proyecto_Belleza/models/models.py (versión recomendada)
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

class SpaServicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    spa_id: Optional[int] = Field(default=None, foreign_key="spa.id")
    servicio_id: Optional[int] = Field(default=None, foreign_key="servicio.id")
    precio: Optional[float] = None
    duracion: Optional[str] = None
    activo: bool = True

    spa: Optional["Spa"] = Relationship(back_populates="servicios_assoc")
    servicio: Optional["Servicio"] = Relationship(back_populates="spas_assoc")


class SpaMaterial(SQLModel, table=True):
    spa_id: Optional[int] = Field(default=None, foreign_key="spa.id", primary_key=True)
    material_id: Optional[int] = Field(default=None, foreign_key="material.id", primary_key=True)
    activo: bool = True

    spa: Optional["Spa"] = Relationship(back_populates="materiales_assoc")
    material: Optional["Material"] = Relationship(back_populates="spas_assoc")


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    correo: str
    contrasena: str
    rol: str = Field(default="cliente")  # 👈 Valor por defecto
    activo: bool = True

    spas: List["Spa"] = Relationship(back_populates="admin_spa")
    resenas: List["Resena"] = Relationship(back_populates="usuario")


class Spa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    direccion: str
    zona: str
    horario: Optional[str] = None
    calificacion_promedio: float = 0.0
    activo: bool = True
    ultima_actualizacion: Optional[date] = None
    desactualizado: bool = False

    admin_spa_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    admin_spa: Optional[Usuario] = Relationship(back_populates="spas")

    servicios_assoc: List[SpaServicio] = Relationship(back_populates="spa")
    materiales_assoc: List[SpaMaterial] = Relationship(back_populates="spa")
    resenas: List["Resena"] = Relationship(back_populates="spa")


class Servicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    duracion_ref: Optional[str] = None
    precio_ref: Optional[float] = None
    activo: bool = True

    spas_assoc: List[SpaServicio] = Relationship(back_populates="servicio")


class Material(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    tipo: Optional[str] = None
    activo: bool = True

    spas_assoc: List[SpaMaterial] = Relationship(back_populates="material")


class Resena(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    calificacion: int
    comentario: str
    fecha_creacion: date = Field(default_factory=lambda: date.today())
    activo: bool = True

    spa_id: Optional[int] = Field(default=None, foreign_key="spa.id")
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")

    spa: Optional[Spa] = Relationship(back_populates="resenas")
    usuario: Optional[Usuario] = Relationship(back_populates="resenas")

class SpaUpdate(SQLModel):
    nombre: str | None = None
    direccion: str | None = None
    zona: str | None = None
    horario: str | None = None
