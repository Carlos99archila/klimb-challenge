from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import database.crud as crud
import database.sql_models as sql_models
import models.py_schemas as py_schemas
from dependencies import get_db, get_current_user
from routers.token_generator import create_access_token
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(tags=["Operaciones"])


# --- Crear operación (solo operadores) ---
@router.post("/operation", response_model=py_schemas.Operation, status_code=status.HTTP_201_CREATED)
async def create_operation(
    operation_data: py_schemas.OperationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user)
) -> py_schemas.Operation:
    # Verificar si el usuario tiene rol de 'operador'
    if current_user.role != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to create an operation.")

    try:
        # Crear la operación
        operation = await crud.create_operation(db, operation_data, current_user)
        return operation

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


""" # --- Listar operaciones activas ---
@router.get("/operations", response_model=List[py_schemas.Operation], status_code=status.HTTP_200_OK)
async def list_active_operations(
    db: AsyncSession = Depends(get_db)
) -> List[py_schemas.Operation]:
    try:
        # Obtener todas las operaciones activas (que no están cerradas y no han alcanzado la fecha límite)
        operations = await crud.get_active_operations(db)
        return operations

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}") """


# --- Eliminar operación (solo operadores) ---
@router.delete("/operation/{operation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operation(
    operation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user)
):
    # Verificar si el usuario tiene rol de 'operador'
    if current_user.role != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete an operation.")

    try:
        # Verificar si la operación existe
        operation = await crud.get_operation_by_id(db, operation_id)
        print(operation)

        if not operation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")

        # Eliminar la operación
        await crud.delete_operation_by_id(db, operation_id)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
