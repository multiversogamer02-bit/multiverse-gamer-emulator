# server/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base  # ← Importación relativa
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class License(Base):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    machine_id = Column(String, unique=True, index=True)
    plan = Column(String)
    valid_until = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    plan_id = Column(String)  # "mensual", "trimestral", "anual"
    status = Column(String)   # "active", "cancelled", "expired"
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    payment_id = Column(String)  # ID del pago en Mercado Pago/PayPal