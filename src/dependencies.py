from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import SessionLocal
import uuid

# Dependencia para obtener una sesión asíncrona de la base de datos
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

# Genera un UUID para identificar la ejecución
def get_execution_id() -> uuid.UUID:
    return uuid.uuid4()
