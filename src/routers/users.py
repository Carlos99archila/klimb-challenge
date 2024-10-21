from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import database.crud as crud
import database.sql_models as sql_models
import models.py_schemas as py_schemas
from dependencies import get_db
from passlib.context import CryptContext
from routers.token_generator import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordRequestForm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["Usuarios"])


# --- Crear usuario ---
@router.post("/user", response_model=py_schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create_data: py_schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> py_schemas.User:
    
    # Verificar si el nombre de usuario ya está registrado
    existing_user = await crud.get_user_by_username(db, user_create_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This username is already registered.")
    
    try:
        # Crear el nuevo usuario
        user = await crud.create_user(db, user_create_data)
        return user

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# --- Login usuario ---
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Aquí usamos OAuth2PasswordRequestForm
    db: AsyncSession = Depends(get_db),
):
    # Verificar si el usuario existe
    user = await crud.get_user_by_username(db, form_data.username)  # form_data.username en lugar de username
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    
    # Verificar la contraseña
    if not pwd_context.verify(form_data.password, user.password_hash):  # form_data.password en lugar de password
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        
    try:
        # Generar el token de acceso
        access_token = create_access_token(data={"sub": user.username, "role": user.role})

        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# --- Eliminar usuario ---
@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, 
    db: AsyncSession = Depends(get_db)
):
    # Verificar si el usuario existe
    existing_user = await crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    try:
        # Eliminar el usuario
        await crud.delete_user_by_id(db, str(user_id))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# --- Leer informacion del usuario ---
@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    
    # Verificar si el nombre de usuario ya está registrado
    existing_user = await crud.get_user_by_id(db, user_id)
        
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
    try:
        # valida la informacion del usuario con el modelo (NOOO retorna el password_hash)
        return py_schemas.User.model_validate(existing_user) 

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
