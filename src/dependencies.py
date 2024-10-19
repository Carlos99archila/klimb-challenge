import os
import uuid
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import database.crud as crud
import models.py_schemas as py_schemas
from database.database import SessionLocal


# --- Manejo de Base de Datos --- #
# Dependencia para obtener una sesión asíncrona de la base de datos
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


# --- Generación de UUID --- #
# Genera un UUID para identificar la ejecución
def get_execution_id() -> uuid.UUID:
    return uuid.uuid4()


# --- Manejo de Tokens JWT --- #
# Configuración del token JWT y el esquema de seguridad OAuth2
#SECRET_KEY = str(os.environ.get("SECRET_KEY")) #con variable de entorno en la nube
SECRET_KEY = str(os.environ.get("SECRET_KEY", "klimb-challenge-key")) #para usar en local 
ALGORITHM = "HS256"

# Dependencia para obtener el token desde el encabezado Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# --- Obtener el Usuario Actual --- #
# Función para obtener el usuario actual a partir del token JWT
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> py_schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodificar el token JWT para extraer la información del usuario
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Obtener el usuario desde la base de datos
    user = await crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception

    return user
