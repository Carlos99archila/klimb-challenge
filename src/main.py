import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import SessionLocal, engine, Base
from routers import user, operations

os.environ["REPOSITORY"] = "klimb-challenge"
os.environ["FOLDER"] = ""

app = FastAPI()

app.include_router(user.router)
app.include_router(operations.router)



# Crear las tablas asíncronamente en el evento de inicio de la app
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()
