# routers/servicio_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from core.auth import get_current_user
from models.models import Servicio, Spa, SpaServicio, Usuario
from models.schemas import ServicioCreate, ServicioRead, AsociarServicio

router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"],
    dependencies=[Depends(get_current_user)]
)

# CREAR SERVICIO
@router.post("/", response_model=ServicioRead, status_code=status.HTTP_201_CREATED)
def crear_servicio(
    servicio_data: ServicioCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol != "admin_principal":
        raise HTTPException(status_code=403, detail="Solo el administrador principal puede crear servicios base.")

    servicio_existente = session.exec(
        select(Servicio).where(Servicio.nombre == servicio_data.nombre)
    ).first()
    if servicio_existente:
        raise HTTPException(status_code=400, detail="Ya existe un servicio con ese nombre")

    if servicio_data.precio_ref is not None and servicio_data.precio_ref <= 0:
        raise HTTPException(status_code=400, detail="El precio debe ser mayor que 0")

    nuevo_servicio = Servicio(**servicio_data.dict())
    session.add(nuevo_servicio)
    session.commit()
    session.refresh(nuevo_servicio)
    return nuevo_servicio


# ASOCIAR SERVICIO A UN SPA
@router.post("/asociar/{spa_id}/{servicio_id}")
def asociar_servicio_a_spa(
    spa_id: int,
    servicio_id: int,
    datos: AsociarServicio,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):

    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    if spa.admin_spa_id != current_user.id and current_user.rol != "admin_principal":
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar este Spa.")

    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    existe = session.exec(
        select(SpaServicio).where(
            (SpaServicio.spa_id == spa_id) &
            (SpaServicio.servicio_id == servicio_id)
        )
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="El servicio ya está asociado a este Spa.")

    nueva_rel = SpaServicio(
        spa_id=spa_id,
        servicio_id=servicio_id,
        precio=datos.precio,
        duracion=datos.duracion,
        activo=True
    )

    session.add(nueva_rel)
    session.commit()

    return {"message": f"Servicio '{servicio.nombre}' asociado al Spa '{spa.nombre}' correctamente."}

# LISTAR TODOS LOS SERVICIOS (GLOBAL)
@router.get("/", response_model=list[ServicioRead])
def listar_servicios(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    servicios = session.exec(select(Servicio)).all()
    return servicios


# LISTAR SERVICIOS POR SPA
@router.get("/por_spa/{spa_id}")
def listar_servicios_por_spa(
    spa_id: int,
    session: Session = Depends(get_session),
):
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    relaciones = session.exec(
        select(SpaServicio).where(SpaServicio.spa_id == spa_id)
    ).all()

    servicios_spa = []
    for rel in relaciones:
        servicio = session.get(Servicio, rel.servicio_id)
        if servicio:
            servicios_spa.append(
                {
                    "servicio": servicio.nombre,
                    "descripcion": servicio.descripcion,
                    "precio": rel.precio,
                    "duracion": rel.duracion,
                }
            )
    return servicios_spa


# ACTUALIZAR SERVICIO
@router.patch("/{servicio_id}", response_model=ServicioRead)
def actualizar_servicio(
    servicio_id: int,
    data: ServicioCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol != "admin_principal":
        raise HTTPException(status_code=403, detail="Solo el administrador principal puede editar servicios base.")

    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    if data.precio_ref is not None and data.precio_ref <= 0:
        raise HTTPException(status_code=400, detail="El precio debe ser mayor que 0")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(servicio, campo, valor)

    session.add(servicio)
    session.commit()
    session.refresh(servicio)
    return servicio


# ELIMINAR SERVICIO (ELIMINACIÓN REAL)
@router.delete("/{servicio_id}")
def eliminar_servicio(
    servicio_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol != "admin_principal":
        raise HTTPException(status_code=403, detail="Solo el administrador principal puede eliminar servicios.")

    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    # Borra asociaciones SpaServicio relacionadas primero (evita FK dangling)
    relaciones = session.exec(
        select(SpaServicio).where(SpaServicio.servicio_id == servicio_id)
    ).all()

    for rel in relaciones:
        session.delete(rel)

    # Ahora borrar el servicio
    session.delete(servicio)
    session.commit()

    return {"message": f"Servicio '{servicio.nombre}' eliminado correctamente."}
