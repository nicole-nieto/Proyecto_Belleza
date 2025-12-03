from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.db import get_session
from models.models import Resena, Usuario, Spa
from models.schemas import ResenaCreate, ResenaRead
from core.auth import get_current_user

router = APIRouter(prefix="/resenas", tags=["Reseñas"])


# ------------------------------------------------
# UTILIDAD: agregar spa_nombre y usuario_nombre
# ------------------------------------------------
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


# ------------------------------------------------
# CREAR RESEÑA
# ------------------------------------------------
@router.post("/", response_model=ResenaRead)
def crear_resena(
    resena_data: ResenaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    # Solo usuarios normales
    if current_user.rol != "usuario":
        raise HTTPException(403, "Solo los usuarios pueden crear reseñas")

    spa = session.get(Spa, resena_data.spa_id)
    if not spa or not spa.activo:
        raise HTTPException(404, "Spa no encontrado o inactivo")

    if not (1 <= resena_data.calificacion <= 5):
        raise HTTPException(400, "La calificación debe estar entre 1 y 5")

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

    return anexar_nombres(nueva, session)


# ------------------------------------------------
# LISTAR RESEÑAS POR SPA (ADMIN / USUARIO)
# ------------------------------------------------
@router.get("/por_spa/{spa_id}", response_model=list[ResenaRead])
def listar_resenas_por_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(404, "Spa no encontrado o inactivo")

    resenas = session.exec(
        select(Resena)
        .where(Resena.spa_id == spa_id)
        .where(Resena.activo == True)
    ).all()

    return [anexar_nombres(r, session) for r in resenas]


# ------------------------------------------------
# LISTAR MIS RESEÑAS (USUARIO)
# ------------------------------------------------
@router.get("/mias", response_model=list[ResenaRead])
def listar_mis_resenas(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    resenas = session.exec(
        select(Resena)
        .where(Resena.usuario_id == current_user.id)
        .where(Resena.activo == True)
    ).all()

    return [anexar_nombres(r, session) for r in resenas]


# ------------------------------------------------
# EDITAR RESEÑA
# ------------------------------------------------
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

    # Permisos corregidos
    if current_user.rol == "usuario" and resena.usuario_id != current_user.id:
        raise HTTPException(403, "No puedes editar reseñas de otros usuarios")

    if not (1 <= data.calificacion <= 5):
        raise HTTPException(400, "La calificación debe estar entre 1 y 5")

    resena.comentario = data.comentario
    resena.calificacion = data.calificacion
    resena.spa_id = data.spa_id

    session.add(resena)
    session.commit()
    session.refresh(resena)

    return anexar_nombres(resena, session)


# ------------------------------------------------
# ELIMINAR RESEÑA (LÓGICO)
# ------------------------------------------------
@router.delete("/{resena_id}")
def eliminar_resena(
    resena_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    resena = session.get(Resena, resena_id)
    if not resena:
        raise HTTPException(404, "Reseña no encontrada")

    # Permisos corregidos
    if current_user.rol == "usuario" and resena.usuario_id != current_user.id:
        raise HTTPException(403, "No puedes eliminar reseñas de otros usuarios")

    resena.activo = False
    session.add(resena)
    session.commit()

    return {"message": f"Reseña #{resena.id} fue desactivada correctamente."}


# ------------------------------------------------
# LISTAR TODAS LAS RESEÑAS (ADMIN)
# ------------------------------------------------
@router.get("/todas_admin", response_model=list[ResenaRead])
def listar_todas_admin(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    if current_user.rol not in ["admin", "admin_principal"]:
        raise HTTPException(403, "Solo administradores pueden ver todas las reseñas")

    resenas = session.exec(select(Resena)).all()


    return [anexar_nombres(r, session) for r in resenas]
