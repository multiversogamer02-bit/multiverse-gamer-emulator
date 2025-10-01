# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from backend import models, database, auth

app = FastAPI(title="Multiverse Auth API")

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if auth.get_user(db, email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed = auth.get_password_hash(password)
    new_user = models.User(email=email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return {"msg": "Usuario creado"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.get("/auth/me")
def read_users_me(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = auth.get_user(db, email)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return {"email": user.email, "is_admin": user.is_admin}