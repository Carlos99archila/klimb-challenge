from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import database.crud as crud
import database.sql_models as sql_models
import models.py_schemas as py_schemas
from dependencies import get_db, get_current_user
from routers.token_generator import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from decimal import Decimal

router = APIRouter(tags=["ofertas"])


# --- Crear ofertas (solo inversores) ---
@router.post("/bid", response_model=py_schemas.Bid, status_code=status.HTTP_201_CREATED)
async def create_bid(
    bid_data: py_schemas.BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user)
) -> py_schemas.Bid:
    
    # Verificar si el usuario tiene rol de 'inversor'
    if current_user.role != "inversor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to create a bid.")

    operation = await crud.get_operation_by_id(db, bid_data.operation_id)

    #verifica si existe la operación
    if not operation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")

    # verifica si la operación esta abierta
    if operation.is_closed == True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation is closed")
    
    # Verifica si la fecha y hora actual permite hacer la oferta 
    if datetime.now(timezone.utc).date() > operation.deadline:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation expired by date and time")
    
    # Verifica si la operacion tiene saldo para ofertar 
    if Decimal(operation.amount_required) < Decimal(bid_data.amount) + Decimal(operation.amount_collected):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount of the bid exceeds the value")
    
    try:
        # Crear oferta
        bid = await crud.create_bid(db, bid_data, current_user)
        
        # Actualizar el valor de amount_collected en la operación
        await crud.update_operation_amount_collected(db, bid_data.operation_id, bid_data.amount)

        return bid

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")