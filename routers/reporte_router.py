# routers/reporte_router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from core.db import get_session
from models.models import Spa, Resena

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

@router.get("/resenas_por_spa")
def resenas_por_spa(session: Session = Depends(get_session)):
    resultados = session.exec(
        select(Spa.nombre, func.count(Resena.id))
        .join(Resena, Resena.spa_id == Spa.id)
        .group_by(Spa.id)
    ).all()

    return [{"spa": nombre, "cantidad": total} for nombre, total in resultados]


@router.get("/promedio_por_spa")
def promedio_por_spa(session: Session = Depends(get_session)):
    resultados = session.exec(
        select(Spa.nombre, func.avg(Resena.calificacion))
        .join(Resena, Resena.spa_id == Spa.id)
        .group_by(Spa.id)
    ).all()

    return [{"spa": nombre, "promedio": round(promedio, 2)} for nombre, promedio in resultados]
