from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.db import get_session
from models.models import Material, Spa, SpaMaterial, Usuario
from models.schemas import MaterialCreate, MaterialRead
from core.auth import get_current_user

router = APIRouter(prefix="/materiales", tags=["Materiales"])

# -------------------- CREAR MATERIAL --------------------
@router.post("/", response_model=MaterialRead)
def crear_material(
    material_data: MaterialCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea un nuevo material o marca (ejemplo: OPI, Masglo, etc.)
    Solo los 'admin_principal' o 'admin_spa' pueden crear materiales.
    """
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado para crear materiales")

    material_existente = session.exec(
        select(Material).where(Material.nombre == material_data.nombre)
    ).first()
    if material_existente:
        raise HTTPException(status_code=400, detail="Ya existe un material con ese nombre")

    nuevo_material = Material.from_orm(material_data)
    session.add(nuevo_material)
    session.commit()
    session.refresh(nuevo_material)
    return nuevo_material


# -------------------- LISTAR TODOS LOS MATERIALES --------------------
@router.get("/", response_model=list[MaterialRead])
def listar_materiales(
    incluir_inactivos: bool = False,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todos los materiales registrados.
    - Todos los usuarios autenticados pueden ver materiales activos.
    - Solo 'admin_principal' puede ver los inactivos.
    """
    if incluir_inactivos and current_user.rol != "admin_principal":
        raise HTTPException(status_code=403, detail="No autorizado para ver materiales inactivos")

    query = select(Material)
    if not incluir_inactivos:
        query = query.where(Material.activo == True)

    materiales = session.exec(query).all()
    return materiales


# -------------------- ASOCIAR MATERIAL A UN SPA --------------------
@router.post("/asociar/{spa_id}/{material_id}")
def asociar_material_a_spa(
    spa_id: int,
    material_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Asocia un material existente a un Spa (relación N:M).
    Solo los 'admin_principal' o 'admin_spa' pueden asociar materiales a spas.
    """
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado para asociar materiales a spas")

    spa = session.get(Spa, spa_id)
    material = session.get(Material, material_id)

    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")
    if not material or not material.activo:
        raise HTTPException(status_code=404, detail="Material no encontrado o inactivo")

    relacion_existente = session.exec(
        select(SpaMaterial).where(
            (SpaMaterial.spa_id == spa_id) & (SpaMaterial.material_id == material_id)
        )
    ).first()
    if relacion_existente:
        raise HTTPException(status_code=400, detail="El material ya está asociado a este Spa")

    nueva_asociacion = SpaMaterial(spa_id=spa_id, material_id=material_id, activo=True)
    session.add(nueva_asociacion)
    session.commit()
    return {"message": f"Material '{material.nombre}' asociado al Spa '{spa.nombre}' correctamente."}


# -------------------- LISTAR MATERIALES POR SPA --------------------
@router.get("/por_spa/{spa_id}")
def listar_materiales_por_spa(
    spa_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Muestra los materiales que usa un Spa específico.
    - Cualquier usuario autenticado puede consultar.
    - Si el Spa está inactivo, no se muestra información.
    """
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado o inactivo")

    asociaciones = session.exec(
        select(SpaMaterial).where(SpaMaterial.spa_id == spa_id, SpaMaterial.activo == True)
    ).all()

    materiales_spa = []
    for rel in asociaciones:
        material = session.get(Material, rel.material_id)
        if material and material.activo:
            materiales_spa.append({
                "nombre": material.nombre,
                "tipo": material.tipo
            })

    return materiales_spa


# -------------------- ACTUALIZAR MATERIAL --------------------
@router.patch("/{material_id}", response_model=MaterialRead)
def actualizar_material(
    material_id: int,
    data: MaterialCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza la información de un material.
    Solo 'admin_principal' o 'admin_spa' pueden actualizar.
    """
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar materiales")

    material = session.get(Material, material_id)
    if not material or not material.activo:
        raise HTTPException(status_code=404, detail="Material no encontrado o inactivo")

    material.nombre = data.nombre or material.nombre
    material.tipo = data.tipo or material.tipo

    session.add(material)
    session.commit()
    session.refresh(material)
    return material


# -------------------- ELIMINAR LÓGICAMENTE --------------------
@router.delete("/{material_id}")
def eliminar_material(
    material_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina lógicamente un material (activo=False).
    Solo 'admin_principal' o 'admin_spa' pueden eliminar materiales.
    """
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar materiales")

    material = session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    material.activo = False
    session.add(material)
    session.commit()
    return {"message": f"Material '{material.nombre}' fue desactivado correctamente."}
