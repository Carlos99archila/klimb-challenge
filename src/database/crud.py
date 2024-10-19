from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import String, and_
from sqlalchemy.sql import func
import uuid
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

import database.sql_models as sql_models
import models.py_schemas as py_schemas


# hash
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to generate a hash of a password
def get_password_hash(password):
    return pwd_context.hash(password)


# --- CREATE ---
# Tabla de usuarios
async def create_user(db: AsyncSession, data: py_schemas.UserCreate) -> py_schemas.User:
    try:
        new_user = sql_models.User(
            id=str(uuid.uuid4()),
            username=data.username,
            password_hash=get_password_hash(data.password),
            role=data.role,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return py_schemas.User.model_validate(new_user)
    except SQLAlchemyError as e:
        print(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

# Tabla de operaciones
async def create_operation(db: AsyncSession, data: py_schemas.OperationCreate, current_user: py_schemas.User) -> py_schemas.Operation:
    try:
        # Asignar correctamente los datos de la operación
        new_operation = sql_models.Operation(
            operator_id=current_user.id,  # El ID del operador que está creando la operación
            amount_required=data.amount_required,  # Monto necesario
            interest_rate=data.interest_rate,  # Tasa de interés
            deadline=data.deadline,  # Fecha límite
            amount_collected=0.0,  # Inicialmente, el monto recaudado es 0
            is_closed=False,  # La operación comienza como abierta
            created_at=datetime.now(timezone.utc),  # Fecha de creación
        )
        db.add(new_operation)
        await db.commit()
        await db.refresh(new_operation)
        return new_operation
    except SQLAlchemyError as e:
        print(f"Error creating the operation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

# Tabla de pujas
async def create_bid(db: AsyncSession, data: py_schemas.BidCreate) -> py_schemas.Bid:
    try:
        new_bid = sql_models.Bid(**data.model_dump())
        db.add(new_bid)
        await db.commit()
        await db.refresh(new_bid)
        return new_bid
    except SQLAlchemyError as e:
        print(f"Error creating the bid: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")


# --- READ ---
# Tabla de usuarios
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[py_schemas.User]:
    try:
        result = await db.execute(select(sql_models.User).filter(sql_models.User.id == user_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        print(f"Error getting user information: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[py_schemas.User]:
    try:
        result = await db.execute(select(sql_models.User).filter(sql_models.User.username == username))
        return result.scalars().first()
    except SQLAlchemyError as e:
        print(f"Error getting user information: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

# Tabla de operaciones
async def get_operation_by_id(db: AsyncSession, operation_id: int) -> Optional[py_schemas.Operation]:
    try:
        result = await db.execute(select(sql_models.Operation).filter(sql_models.Operation.id == operation_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        print(f"Error getting operation information: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

# Tabla de pujas
async def get_bid_by_id(db: AsyncSession, bid_id: int) -> Optional[py_schemas.Bid]:
    try:
        result = await db.execute(select(sql_models.Bid).filter(sql_models.Bid.id == bid_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
            print(f"Error getting bid information: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")


# --- DELETE ---
# Tabla de usuarios
async def delete_user_by_id(db: AsyncSession, user_id: str) -> bool:
    try:
        result = await db.execute(select(sql_models.User).filter(sql_models.User.id == user_id))
        user = result.scalars().first()
        if user is None:
            return False
        await db.delete(user)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
# Tabla de operaciones
async def delete_operation_by_id(db: AsyncSession, operation_id: int) -> bool:
    try:
        result = await db.execute(select(sql_models.Operation).filter(sql_models.Operation.id == operation_id))
        operation = result.scalars().first()
        if operation is None:
            return False
        await db.delete(operation)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Error deleting operation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
# Tabla de pujas
async def delete_bid_by_id(db: AsyncSession, bid_id: int) -> bool:
    try:
        result = await db.execute(select(sql_models.Bid).filter(sql_models.Bid.id == bid_id))
        bid = result.scalars().first()
        if bid is None:
            return False
        await db.delete(bid)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Error deleting bid: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")


# --- UPDATE ---
# Tabla de usuarios
async def update_user_by_id(db: AsyncSession, user_id: int, property_name: str, value: str) -> bool:
    try:
        result = await db.execute(select(sql_models.User).filter(sql_models.User.id == user_id))
        user = result.scalars().first()
        if user and hasattr(user, property_name):
            setattr(user, property_name, value)
            await db.commit()
            await db.refresh(user)
            return True
        return False
    except SQLAlchemyError as e:
        print(f"Error updating user information: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    
# Tabla de operaciones
async def update_operation_by_id(db: AsyncSession, operation_id: int, property_name: str, value: str) -> bool:
    try:
        result = await db.execute(select(sql_models.Operation).filter(sql_models.Operation.id == operation_id))
        operation = result.scalars().first()
        if operation and hasattr(operation, property_name):
            setattr(operation, property_name, value)
            await db.commit()
            await db.refresh(operation)
            return True
        return False
    except SQLAlchemyError as e:
        print(f"Error updating operation information: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    
# Tabla de pujas
async def update_bid_by_id(db: AsyncSession, bid_id: int, property_name: str, value: str) -> bool:
    try:
        result = await db.execute(select(sql_models.Bid).filter(sql_models.Bid.id == bid_id))
        bid = result.scalars().first()
        if bid and hasattr(bid, property_name):
            setattr(bid, property_name, value)
            await db.commit()
            await db.refresh(bid)
            return True
        return False
    except SQLAlchemyError as e:
        print(f"Error updating bid information: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")