# routers/spa_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.models import Spa, Usuario
from models.schemas import SpaCreate, SpaRead, SpaUpdate, SpaDetalleRead
from core.auth import get_current_user, admin_spa_required, admin_principal_required
from datetime import date

router = APIRouter(
    prefix="/spas",
    tags=["Spas"]
)


# -------------------- CREAR SPA --------------------
@router.post("/", response_model=SpaRead, status_code=status.HTTP_201_CREATED)
def crear_spa(
    spa_data: SpaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(admin_principal_required)
):

    spa_existente = session.exec(select(Spa).where(Spa.nombre == spa_data.nombre)).first()
    if spa_existente:
        raise HTTPException(status_code=400, detail="Ya existe un spa con ese nombre")

    nuevo_spa = Spa(
        nombre=spa_data.nombre,
        direccion=spa_data.direccion,
        zona=spa_data.zona,
        horario=spa_data.horario,
        ultima_actualizacion=date.today(),
        admin_spa_id=current_user.id if current_user.rol == "admin_spa" else None
    )

    session.add(nuevo_spa)
    session.commit()
    session.refresh(nuevo_spa)
    return nuevo_spa


# -------------------- LISTAR SPAS --------------------
@router.get("/", response_model=list[SpaRead])
def listar_spas(
    incluir_inactivos: bool = False,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    if current_user.rol == "admin_principal":
        if incluir_inactivos:
            spas = session.exec(select(Spa)).all()
        else:
            spas = session.exec(select(Spa).where(Spa.activo == True)).all()
        return spas
    
    if current_user.rol == "admin_spa":
        spas = session.exec(select(Spa).where(
            (Spa.activo == True) | 
            (Spa.admin_spa_id == current_user.id)
        )).all()
        return spas
    
    spas = session.exec(select(Spa).where(Spa.activo == True)).all()
    return spas



# -------------------- VER SPA --------------------
@router.get("/{spa_id}", response_model=SpaDetalleRead)
def obtener_spa(
    spa_id: int,
    session: Session = Depends(get_session),
):
    spa = session.get(Spa, spa_id)

    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    # Obtener servicios del spa con detalle
    servicios = []
    for assoc in spa.servicios_assoc:
        if assoc.activo:
            servicios.append({
                "id": assoc.id,
                "servicio_id": assoc.servicio.id,
                "nombre": assoc.servicio.nombre,
                "descripcion": assoc.servicio.descripcion,
                "precio": assoc.precio,
                "duracion": assoc.duracion,
            })

    # Obtener materiales
    materiales = []
    for assoc in spa.materiales_assoc:
        if assoc.activo:
            materiales.append({
                "id": assoc.material.id,
                "nombre": assoc.material.nombre,
                "tipo": assoc.material.tipo
            })

    # Obtener reseñas
    resenas = []
    for r in spa.resenas:
        if r.activo:
            resenas.append({
                "id": r.id,
                "calificacion": r.calificacion,
                "comentario": r.comentario,
                "fecha_creacion": r.fecha_creacion,
                "usuario_id": r.usuario_id,
                "usuario_nombre": r.usuario.nombre if r.usuario else None,
            })

    # Devolver todo
    return {
        "id": spa.id,
        "nombre": spa.nombre,
        "direccion": spa.direccion,
        "zona": spa.zona,
        "horario": spa.horario,
        "calificacion_promedio": spa.calificacion_promedio,
        "ultima_actualizacion": spa.ultima_actualizacion,
        "servicios": servicios,
        "materiales": materiales,
        "resenas": resenas
    }



# -------------------- EDITAR SPA --------------------
@router.patch("/{spa_id}", response_model=SpaRead)
def actualizar_spa(
    spa_id: int,
    spa_data: SpaUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    # admin_spa — solo su propio spa
    if current_user.rol == "admin_spa" and spa.admin_spa_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para editar este spa")

    for campo, valor in spa_data.dict(exclude_unset=True).items():
        setattr(spa, campo, valor)

    spa.ultima_actualizacion = date.today()

    session.commit()
    session.refresh(spa)
    return spa

# -------------------- DESACTIVAR SPA --------------------
@router.delete("/{spa_id}")
def eliminar_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(admin_principal_required)
):
    spa = session.get(Spa, spa_id)
    if not spa:
        raise HTTPException(status_code=404, detail="Spa no encontrado")

    spa.activo = False
    session.commit()
    return {"message": f"Spa '{spa.nombre}' fue desactivado correctamente."}


# -------------------- BUSCAR SPA --------------------
@router.get("/buscar/", response_model=list[SpaRead])
def buscar_spa(
    nombre: str | None = None,
    zona: str | None = None,
    session: Session = Depends(get_session),
):
    """
    Este endpoint es público (no requiere login).
    Perfecto para clientes.
    """

    query = select(Spa).where(Spa.activo == True)

    if nombre:
        query = query.where(Spa.nombre.contains(nombre))
    if zona:
        query = query.where(Spa.zona.contains(zona))

    spas = session.exec(query).all()
    return spas


# -------------------- RESTAURAR SPA --------------------
@router.patch("/{spa_id}/restore")
def restore_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(admin_principal_required)
):
    spa = session.get(Spa, spa_id)
    if not spa:
        raise HTTPException(status_code=404, detail="Spa no encontrado")
    
    spa.activo = True
    spa.ultima_actualizacion = date.today()

    session.commit()
    session.refresh(spa)

    return {"message": f"Spa '{spa.nombre}' restaurado correctamente."}
