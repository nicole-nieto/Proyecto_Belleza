from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.db import get_session
from models.models import Resena, Usuario, Spa
from models.schemas import ResenaCreate, ResenaRead
from core.auth import get_current_user

router = APIRouter(prefix="/resenas", tags=["Reseñas"])

# ==========================
# FUNCIÓN PARA RE-CALCULAR
# ==========================
def recalcular_calificacion_spa(spa: Spa, session: Session):
    reseñas_activas = [r.calificacion for r in spa.resenas if r.activo]

    if not reseñas_activas:
        spa.calificacion_promedio = 0
    else:
        spa.calificacion_promedio = sum(reseñas_activas) / len(reseñas_activas)

    session.add(spa)

# ==============================
# UTILIDAD: anexar nombres
# ==============================
def anexar_nombres(resena: Resena, session: Session) -> ResenaRead:
    spa = session.get(Spa, resena.spa_id)
    usuario = session.get(Usuario, resena.usuario_id)

    return ResenaRead(
        id=resena.id,
        calificacion=resena.calificacion,
        comentario=resena.comentario,
        fecha_creacion=resena.fecha_creacion,
        spa_id=resena.spa_id,
        spa_nombre=spa.nombre if spa else None,
        usuario_id=resena.usuario_id,
        usuario_nombre=usuario.nombre if usuario else None,
    )

# ==============================
# CREAR RESEÑA
# ==============================
@router.post("/", response_model=ResenaRead)
def crear_resena(
    resena_data: ResenaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "usuario":
        raise HTTPException(403, "Solo los usuarios pueden crear reseñas")

    spa = session.get(Spa, resena_data.spa_id)
    if not spa or not spa.activo:
        raise HTTPException(404, "Spa no encontrado o inactivo")

    nueva = Resena(
        calificacion=resena_data.calificacion,
        comentario=resena_data.comentario,
        spa_id=resena_data.spa_id,
        usuario_id=current_user.id,
        activo=True,
    )
    session.add(nueva)
    session.commit()
    session.refresh(nueva)

    recalcular_calificacion_spa(spa, session)
    session.commit()

    return anexar_nombres(nueva, session)

# ==============================
# EDITAR RESEÑA
# ==============================
@router.patch("/{resena_id}", response_model=ResenaRead)
def actualizar_resena(
    resena_id: int,
    data: ResenaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    resena = session.get(Resena, resena_id)
    if not resena or not resena.activo:
        raise HTTPException(404, "Reseña no encontrada o inactiva")

    if current_user.rol == "usuario" and resena.usuario_id != current_user.id:
        raise HTTPException(403, "No puedes editar reseñas de otros usuarios")

    resena.calificacion = data.calificacion
    resena.comentario = data.comentario
    resena.spa_id = data.spa_id

    session.add(resena)
    spa = session.get(Spa, resena.spa_id)

    recalcular_calificacion_spa(spa, session)
    session.commit()
    session.refresh(resena)

    return anexar_nombres(resena, session)

# ==============================
# ELIMINAR RESEÑA (LÓGICO)
# ==============================
@router.delete("/{resena_id}")
def eliminar_resena(
    resena_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    resena = session.get(Resena, resena_id)
    if not resena:
        raise HTTPException(404, "Reseña no encontrada")

    if current_user.rol == "usuario" and resena.usuario_id != current_user.id:
        raise HTTPException(403, "No puedes eliminar reseñas de otros usuarios")

    resena.activo = False
    session.add(resena)

    spa = session.get(Spa, resena.spa_id)
    recalcular_calificacion_spa(spa, session)

    session.commit()

    return {"message": "Reseña eliminada correctamente"}
