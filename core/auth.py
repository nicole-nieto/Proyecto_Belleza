from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from core.db import get_session
from models.models import Usuario
from fastapi.security import OAuth2PasswordBearer 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------- CONFIGURACIÓN GENERAL ----------------
SECRET_KEY = "super_clave_secreta_nicole_2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- UTILIDADES ----------------
def hash_password(password: str):
    """Encripta una contraseña usando bcrypt (truncando a 72 bytes)."""
    password_bytes = password.encode("utf-8")[:72]  # truncar a 72 bytes
    return pwd_context.hash(password_bytes)

def verify_password(password: str, hashed_password: str):
    """Verifica que la contraseña ingresada coincida con la guardada (truncando a 72 bytes)."""
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.verify(password_bytes, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT con expiración."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- DEPENDENCIA PRINCIPAL ----------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    """Valida el token y devuelve el usuario actual."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o no proporcionado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(Usuario, int(user_id))
    if user is None or not user.activo:
        raise credentials_exception

    return user

# ---------------- LOGIN ----------------
def login_user(correo: str, contrasena: str, session: Session):
    """Autentica al usuario y genera un token JWT."""
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")
    if not verify_password(contrasena, usuario.contrasena):
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    access_token = create_access_token(data={"sub": str(usuario.id), "rol": usuario.rol})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": usuario.rol,
        "message": f"Inicio de sesión exitoso como {usuario.rol}",
    }

# ---------------- DEPENDENCIAS DE AUTORIZACIÓN ----------------
def admin_principal_required(current_user=Depends(get_current_user)):
    if current_user.rol != "admin_principal":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo el administrador principal puede realizar esta acción.",
        )
    return current_user

def admin_spa_required(current_user=Depends(get_current_user)):
    if current_user.rol not in ["admin_principal", "admin_spa"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores de spa o el administrador principal pueden realizar esta acción.",
        )
    return current_user

def usuario_required(current_user=Depends(get_current_user)):
    if current_user.rol != "usuario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo los usuarios pueden realizar esta acción.",
        )
    return current_user
