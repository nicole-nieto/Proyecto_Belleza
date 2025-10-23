from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func, text
from core.db import get_session
from models.models import Spa, Servicio, Material, Usuario, Resena, SpaServicio
from core.auth import get_current_user, admin_principal_required

router = APIRouter(prefix="/reportes", tags=["Reportes"])


# -------------------- REPORTE GENERAL --------------------
@router.get("/general")
def reporte_general(
    session: Session = Depends(get_session),
    _: Usuario = Depends(admin_principal_required),
):
    """
    Muestra estadísticas generales del sistema.
    Solo accesible por el administrador principal.
    """
    total_usuarios = session.exec(select(func.count(Usuario.id))).one()
    total_spas = session.exec(select(func.count(Spa.id))).one()
    total_servicios = session.exec(select(func.count(Servicio.id))).one()
    total_materiales = session.exec(select(func.count(Material.id))).one()
    total_resenas = session.exec(select(func.count(Resena.id))).one()

    return {
        "usuarios": total_usuarios,
        "spas": total_spas,
        "servicios": total_servicios,
        "materiales": total_materiales,
        "resenas": total_resenas,
    }


# -------------------- REPORTE POR SPA --------------------
@router.get("/por_spa/{spa_id}")
def reporte_por_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(admin_principal_required),
):
    """
    Muestra un reporte específico de un Spa:
    - Número de servicios asociados
    - Número de reseñas
    - Calificación promedio
    """
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    # Contar servicios asociados al spa (usando la tabla intermedia SpaServicio)
    total_servicios = session.exec(
        select(func.count(SpaServicio.servicio_id)).where(SpaServicio.spa_id == spa_id)
    ).one()

    # Contar reseñas del spa
    total_resenas = session.exec(
        select(func.count(Resena.id)).where(Resena.spa_id == spa_id)
    ).one()

    # Calcular calificación promedio
    promedio = session.exec(
        select(func.avg(Resena.calificacion)).where(Resena.spa_id == spa_id)
    ).one()

    return {
        "spa": spa.nombre,
        "total_servicios": total_servicios,
        "total_resenas": total_resenas,
        "calificacion_promedio": round(promedio or 0, 2),
    }


# -------------------- REPORTE DE USUARIOS --------------------
@router.get("/usuarios")
def reporte_usuarios(
    session: Session = Depends(get_session),
    _: Usuario = Depends(admin_principal_required),
):
    """
    Reporte con el número de usuarios activos e inactivos.
    """
    activos = session.exec(select(func.count(Usuario.id)).where(Usuario.activo == True)).one()
    inactivos = session.exec(select(func.count(Usuario.id)).where(Usuario.activo == False)).one()

    return {
        "usuarios_activos": activos,
        "usuarios_inactivos": inactivos,
        "total": activos + inactivos,
    }


# -------------------- REPORTE DE SERVICIOS POPULARES --------------------
@router.get("/servicios_populares")
def reporte_servicios_populares(
    session: Session = Depends(get_session),
    _: Usuario = Depends(admin_principal_required),
):
    """
    Reporte de servicios más populares (por número de spas que lo ofrecen).
    """
    query = text("""
        SELECT s.id, s.nombre, COUNT(ss.spa_id) AS cantidad_spas
        FROM servicio s
        JOIN spaservicio ss ON s.id = ss.servicio_id
        WHERE s.activo = 1 AND ss.activo = 1
        GROUP BY s.id
        ORDER BY cantidad_spas DESC
    """)

    resultados = session.exec(query).all()

    servicios = [
        {"id": r[0], "nombre": r[1], "cantidad_spas": r[2]} for r in resultados
    ]

    return {"servicios_populares": servicios}

