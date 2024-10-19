import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Conexion red
# connection_string = os.environ.get("DB_INSTANCE_KLIMB_MYSQL")

# Conexion local a la base de datos MySQL en WampServer
connection_string = os.environ.get(
    "DB_INSTANCE_KLIMB_MYSQL", default="mysql+asyncmy://root:@localhost/klimb_challenge"
)

# Crear el motor asíncrono para conectar a la base de datos
engine = create_async_engine(
    connection_string,
    pool_recycle=3600,
    pool_pre_ping=True,
)

# Crear la clase SessionLocal para manejar las sesiones con la base de datos
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()