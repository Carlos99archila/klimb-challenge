from sqlalchemy import (
    Column,
    DECIMAL,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    TIMESTAMP,
    Boolean,
    VARCHAR,
)
from sqlalchemy.orm import relationship
from database.database import Base  

# Tabla de usuarios (usuarios que pueden ser operadores o inversores)
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)  
    role = Column(String(20), nullable=False)  
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    bids = relationship("Bid", back_populates="user")

# Tabla de operaciones financieras creadas por los operadores
class Operation(Base):
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operator_id = Column(String(36), ForeignKey("users.id"), nullable=False) 
    amount_required = Column(DECIMAL(15, 2), nullable=False)  
    interest_rate = Column(Float, nullable=False)  
    deadline = Column(Date, nullable=False)  
    amount_collected = Column(DECIMAL(15, 2), default=0)  
    is_closed = Column(Boolean, default=False)  
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    bids = relationship("Bid", back_populates="operation")

# Tabla de pujas realizadas por los inversores
class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False)  
    investor_id = Column(String(36), ForeignKey("users.id"), nullable=False)  
    amount = Column(DECIMAL(15, 2), nullable=False)  
    interest_rate = Column(Float, nullable=False)  
    bid_date = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    user = relationship("User", back_populates="bids")
    operation = relationship("Operation", back_populates="bids")
