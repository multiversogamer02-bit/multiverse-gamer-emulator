# server/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from .database import Base
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
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    machine_id = Column(String, index=True)
    plan = Column(String)
    valid_until = Column(DateTime(timezone=True))  # ← ¡timezone=True!
    is_active = Column(Boolean, default=True)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    token = Column(String, unique=True)
    expires_at = Column(DateTime)