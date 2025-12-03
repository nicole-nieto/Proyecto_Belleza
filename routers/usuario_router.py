from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.models import Usuario
from models.schemas import UsuarioCreate, UsuarioRead
from core.auth import hash_password, get_current_user, admin_principal_required
import templates
from fastapi.requests import Request

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(get_current_user)]  # 👈 Todos deben estar autenticados
)
@router.get("/usuarios", dependencies=[Depends(admin_principal_required)])


@router.get("/perfil")
def perfil_usuario(request: Request, current_user: Usuario = Depends(get_current_user)):
    if current_user.role != "user":  # Solo usuarios normales
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return templates.TemplateResponse("perfil.html", {"request": request, "user": current_user})

# -------------------- CREAR ADMINISTRADOR DE SPA --------------------
@router.post("/crear_admin_spa", response_model=UsuarioRead)
def crear_admin_spa(
    usuario_data: UsuarioCreate,
    session: Session = Depends(get_session),
    current_user=Depends(admin_principal_required),
):
    """
    Solo el administrador principal puede crear administradores de spa.
    """
    usuario_existente = session.exec(
        select(Usuario).where(Usuario.correo == usuario_data.correo)
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = hash_password(usuario_data.contrasena)
    nuevo_admin = Usuario(
        nombre=usuario_data.nombre,
        correo=usuario_data.correo,
        contrasena=hashed_password,
        rol="admin_spa",
        activo=True,
    )

    session.add(nuevo_admin)
    session.commit()
    session.refresh(nuevo_admin)
    return nuevo_admin


# -------------------- LISTAR USUARIOS --------------------
@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(
    session: Session = Depends(get_session),
    current_user=Depends(admin_principal_required)
):
    """
    Lista todos los usuarios registrados (solo admin principal).
    """
    usuarios = session.exec(select(Usuario)).all()
    return usuarios


# -------------------- OBTENER USUARIO POR ID --------------------
@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve la información de un usuario específico.
    - Los usuarios pueden ver su propio perfil.
    - admin_principal puede ver cualquier usuario.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if current_user.rol != "admin_principal" and current_user.id != usuario.id:
        raise HTTPException(status_code=403, detail="No autorizado para ver este usuario")

    return usuario


# -------------------- DESACTIVAR USUARIO --------------------
@router.patch("/desactivar/{usuario_id}")
def desactivar_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(admin_principal_required),
):
    """
    Permite al administrador principal desactivar un usuario.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = False
    session.add(usuario)
    session.commit()
    return {"message": f"El usuario '{usuario.nombre}' ha sido desactivado correctamente."}

# -------------------- REACTIVAR USUARIO --------------------
@router.patch("/activar/{usuario_id}")
def activar_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(admin_principal_required),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = True
    session.add(usuario)
    session.commit()
    return {"message": f"El usuario '{usuario.nombre}' ha sido activado correctamente."}

