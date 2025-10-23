from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlmodel import Session, select
from core.db import get_session
from core.auth import hash_password, verify_password, create_access_token
from models.models import Usuario
from models.schemas import UsuarioCreate

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# -------------------- REGISTRO DE USUARIO --------------------
@router.post("/register")
def register(usuario_data: UsuarioCreate, session: Session = Depends(get_session)):
    """
    Registra un nuevo usuario con rol 'usuario' por defecto.
    """
    # Verificar si el correo ya está registrado
    usuario_existente = session.exec(
        select(Usuario).where(Usuario.correo == usuario_data.correo)
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Hash de la contraseña
    hashed_password = hash_password(usuario_data.contrasena)

    # Crear el nuevo usuario
    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        correo=usuario_data.correo,
        contrasena=hashed_password,
        rol="usuario",  # 👈 por defecto, siempre usuario
        activo=True
    )

    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return {"message": f"Usuario {nuevo_usuario.nombre} registrado exitosamente"}


# -------------------- LOGIN --------------------

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    correo = form_data.username  # 👈 Swagger usa 'username' en lugar de 'correo'
    contrasena = form_data.password

    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")

    if not verify_password(contrasena, usuario.contrasena):
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")

    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    access_token = create_access_token(
        data={"sub": str(usuario.id), "rol": usuario.rol}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": usuario.rol,
        "message": f"Inicio de sesión exitoso como {usuario.rol}"
    }


# -------------------- CREAR ADMIN PRINCIPAL (SOLO 1 VEZ) --------------------
@router.post("/setup_admin")
def setup_admin(session: Session = Depends(get_session)):
    """
    Crea el primer administrador principal del sistema.
    Solo se debe ejecutar una vez (ejemplo: Nicole).
    """
    admin_existente = session.exec(
        select(Usuario).where(Usuario.rol == "admin_principal")
    ).first()

    if admin_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un administrador principal registrado."
        )

    contrasena_inicial = "admin123"  # ⚠️ cámbiala después del primer login
    hashed_password = hash_password(contrasena_inicial)

    nuevo_admin = Usuario(
        nombre="Nicole",
        correo="nicole@admin.com",
        contrasena=hashed_password,
        rol="admin_principal",
        activo=True
    )

    session.add(nuevo_admin)
    session.commit()
    session.refresh(nuevo_admin)

    return {
        "message": "Administrador principal creado exitosamente.",
        "correo": nuevo_admin.correo,
        "contrasena_temporal": contrasena_inicial
    }
