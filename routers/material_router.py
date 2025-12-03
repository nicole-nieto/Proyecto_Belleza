from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.db import get_session
from models.models import Material, Spa, SpaMaterial, Usuario
from models.schemas import MaterialCreate, MaterialRead, MaterialUpdate
from core.auth import get_current_user

router = APIRouter(prefix="/materiales", tags=["Materiales"])

# -------------------- CREAR MATERIAL --------------------
@router.post("/", response_model=MaterialRead)
def crear_material(
    material_data: MaterialCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado")

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


# -------------------- LISTAR --------------------
@router.get("/", response_model=list[MaterialRead])
def listar_materiales(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    return session.exec(select(Material)).all()


# -------------------- ASOCIAR A SPA --------------------
@router.post("/asociar/{spa_id}/{material_id}")
def asociar_material_a_spa(
    spa_id: int,
    material_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    spa = session.get(Spa, spa_id)
    material = session.get(Material, material_id)

    if not spa:
        raise HTTPException(status_code=404, detail="Spa no encontrado")

    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    existe = session.exec(
        select(SpaMaterial).where(
            (SpaMaterial.spa_id == spa_id) &
            (SpaMaterial.material_id == material_id)
        )
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="El material ya está asociado al spa")

    nueva = SpaMaterial(spa_id=spa_id, material_id=material_id)
    session.add(nueva)
    session.commit()
    return {"message": "Material asociado correctamente"}


# -------------------- ACTUALIZAR --------------------
@router.patch("/{material_id}", response_model=MaterialRead)
def actualizar_material(
    material_id: int,
    data: MaterialUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    material = session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    material.nombre = data.nombre or material.nombre
    material.tipo = data.tipo or material.tipo

    session.add(material)
    session.commit()
    session.refresh(material)
    return material


# -------------------- ELIMINAR REAL --------------------
@router.delete("/{material_id}")
def eliminar_material(
    material_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    material = session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    # Borrar relaciones primero
    session.exec(
        select(SpaMaterial).where(SpaMaterial.material_id == material_id)
    ).all()

    asociaciones = session.exec(
        select(SpaMaterial).where(SpaMaterial.material_id == material_id)
    )
    for rel in asociaciones:
        session.delete(rel)

    # Borrar material
    session.delete(material)
    session.commit()

    return {"message": "Material eliminado definitivamente."}

# LISTAR MATERIALES POR SPA
@router.get("/por_spa/{spa_id}")
def materiales_por_spa(
    spa_id: int,
    session: Session = Depends(get_session)
):
    spa = session.get(Spa, spa_id)
    if not spa or not spa.activo:
        raise HTTPException(status_code=404, detail="Spa no encontrado")

    relaciones = session.exec(
        select(SpaMaterial).where(SpaMaterial.spa_id == spa_id)
    ).all()

    materiales = []
    for rel in relaciones:
        mat = session.get(Material, rel.material_id)
        if mat:
            materiales.append({
                "id": mat.id,
                "nombre": mat.nombre,
                "tipo": mat.tipo
            })

    return materiales
