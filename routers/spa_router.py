from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.models import Spa, Usuario
from models.schemas import SpaCreate, SpaRead
from core.auth import get_current_user, admin_spa_required, admin_principal_required
from datetime import date

# ✅ Todos los endpoints de este router exigen autenticación
router = APIRouter(
    prefix="/spas",
    tags=["Spas"],
    dependencies=[Depends(get_current_user)]  # 👈 Esto fuerza autenticación global en este módulo
)

# -------------------- CREAR SPA --------------------
@router.post("/", response_model=SpaRead, status_code=status.HTTP_201_CREATED)
def crear_spa(
    spa_data: SpaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(admin_principal_required)
):
    """
    Crea un nuevo Spa (solo para admin_principal).
    """
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


# -------------------- LISTAR TODOS LOS SPAS --------------------
@router.get("/", response_model=list[SpaRead])
def listar_spas(
    incluir_inactivos: bool = False,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos los Spas activos (requiere estar autenticado).
    Si 'incluir_inactivos=True', solo los admin_principal pueden verlos.
    """
    if incluir_inactivos:
        if current_user.rol != "admin_principal":
            raise HTTPException(status_code=403, detail="No autorizado para ver spas inactivos")
        spas = session.exec(select(Spa)).all()
    else:
        spas = session.exec(select(Spa).where(Spa.activo == True)).all()

    return spas


# -------------------- OBTENER SPA POR ID --------------------
@router.get("/{spa_id}", response_model=SpaRead)
def obtener_spa(
    spa_id: int,
    session: Session = Depends(get_session)
):
    """
    Devuelve la información de un Spa específico (requiere autenticación).
    """
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")
    return spa


# -------------------- ACTUALIZAR SPA --------------------
@router.patch("/{spa_id}", response_model=SpaRead)
def actualizar_spa(
    spa_id: int,
    spa_data: SpaCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza la información de un Spa.
    - admin_principal puede modificar cualquier spa.
    - admin_spa solo puede modificar su propio spa.
    """
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    # Autorización
    if current_user.rol == "admin_spa" and spa.admin_spa_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para editar este spa")

    # Actualizar campos enviados
    for campo, valor in spa_data.dict(exclude_unset=True).items():
        setattr(spa, campo, valor)

    spa.ultima_actualizacion = date.today()

    session.add(spa)
    session.commit()
    session.refresh(spa)
    return spa


# -------------------- ELIMINAR (LÓGICAMENTE) SPA --------------------
@router.delete("/{spa_id}")
def eliminar_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(admin_principal_required)
):
    """
    Elimina lógicamente un Spa (solo admin_principal).
    """
    spa = session.get(Spa, spa_id)
    if not spa:
        raise HTTPException(status_code=404, detail="Spa no encontrado")

    spa.activo = False
    session.add(spa)
    session.commit()
    return {"message": f"Spa '{spa.nombre}' fue desactivado correctamente."}


# -------------------- BUSCAR SPA POR NOMBRE O ZONA --------------------
@router.get("/buscar/", response_model=list[SpaRead])
def buscar_spa(
    nombre: str | None = None,
    zona: str | None = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    
    query = select(Spa).where(Spa.activo == True)

    if nombre:
        query = query.where(Spa.nombre.contains(nombre))
    if zona:
        query = query.where(Spa.zona.contains(zona))

    spas = session.exec(query).all()
    if not spas:
        raise HTTPException(status_code=404, detail="No se encontraron spas con esos criterios.")
    return spas
