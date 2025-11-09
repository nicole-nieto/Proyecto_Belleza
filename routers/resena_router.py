from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.models import Resena, Usuario, Spa
from models.schemas import ResenaCreate, ResenaRead
from core.auth import get_current_user

router = APIRouter(prefix="/resenas", tags=["Reseñas"])

# -------------------- CREAR RESEÑA --------------------
@router.post("/", response_model=ResenaRead)
def crear_resena(
    resena_data: ResenaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva reseña para un Spa.
    - Solo los usuarios con rol 'usuario' pueden crear reseñas.
    - El Spa debe existir y estar activo.
    - La calificación debe estar entre 1 y 5.
    """
    if current_user.rol != "usuario":
        raise HTTPException(status_code=403, detail="Solo los clientes pueden crear reseñas")

    spa = session.get(Spa, resena_data.spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    if not (1 <= resena_data.calificacion <= 5):
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5")

    nueva_resena = Resena(
        calificacion=resena_data.calificacion,
        comentario=resena_data.comentario,
        spa_id=resena_data.spa_id,
        usuario_id=current_user.id,
        activo=True,
    )
    session.add(nueva_resena)
    session.commit()
    session.refresh(nueva_resena)
    return nueva_resena


# -------------------- LISTAR RESEÑAS POR SPA --------------------
@router.get("/por_spa/{spa_id}", response_model=list[ResenaRead])
def listar_resenas_por_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Muestra las reseñas activas de un Spa específico.
    - Cualquier usuario autenticado puede consultar.
    """
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    resenas = session.exec(
        select(Resena)
        .where(Resena.spa_id == spa_id)
        .where(Resena.activo == True)
    ).all()

    return resenas


# -------------------- LISTAR RESEÑAS DEL USUARIO ACTUAL --------------------
@router.get("/mias", response_model=list[ResenaRead])
def listar_mis_resenas(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Muestra solo las reseñas creadas por el usuario autenticado.
    """
    resenas = session.exec(
        select(Resena)
        .where(Resena.usuario_id == current_user.id)
        .where(Resena.activo == True)
    ).all()
    return resenas


# -------------------- ACTUALIZAR RESEÑA --------------------
@router.patch("/{resena_id}", response_model=ResenaRead)
def actualizar_resena(
    resena_id: int,
    data: ResenaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza una reseña.
    - El usuario solo puede modificar sus propias reseñas.
    - Los administradores pueden modificar cualquiera.
    """
    resena = session.get(Resena, resena_id)
    if not resena or not resena.activo:
        raise HTTPException(status_code=404, detail="Reseña no encontrada o inactiva")

    if current_user.rol == "cliente" and resena.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes editar reseñas de otros usuarios")

    if data.calificacion and not (1 <= data.calificacion <= 5):
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5")

    resena.comentario = data.comentario or resena.comentario
    resena.calificacion = data.calificacion or resena.calificacion

    session.add(resena)
    session.commit()
    session.refresh(resena)
    return resena


# -------------------- ELIMINAR LÓGICAMENTE RESEÑA --------------------
@router.delete("/{resena_id}")
def eliminar_resena(
    resena_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina lógicamente una reseña (activo=False).
    - El usuario solo puede eliminar sus propias reseñas.
    - Los administradores pueden eliminar cualquiera.
    """
    resena = session.get(Resena, resena_id)
    if not resena:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    if current_user.rol == "cliente" and resena.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar reseñas de otros usuarios")

    resena.activo = False
    session.add(resena)
    session.commit()
    return {"message": f"Reseña #{resena.id} fue desactivada correctamente."}
