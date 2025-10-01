# server/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
<<<<<<< HEAD
from server import models, database
=======
import database
>>>>>>> bf4c56320f757b6b8bf8010df1b9067d2e71a9a6
import os

app = FastAPI(title="Multiverse Gamer API")

<<<<<<< HEAD
# 👇 Crear tablas al iniciar (reemplaza database.init_db())
models.Base.metadata.create_all(bind=database.engine)
=======
# Inicializar base de datos
database.init_db()
>>>>>>> bf4c56320f757b6b8bf8010df1b9067d2e71a9a6

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "multiverse_secret_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class PaymentRequest(BaseModel):
    email: str
    plan: str

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    return db.query(database.User).filter(database.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token( dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user(db, email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed = get_password_hash(password)
    new_user = database.User(email=email, hashed_password=hashed, is_admin=(email == "rodrigoaguirre196@gmail.com"))
    db.add(new_user)
    db.commit()
    return {"msg": "Usuario creado"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/validate-license")
def validate_license(machine_id: str, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    license = db.query(database.License).filter(
        database.License.machine_id == machine_id,
        database.License.user_id == current_user.id,
        database.License.is_active == True
    ).first()
    if not license or datetime.now(timezone.utc) > license.valid_until:
        raise HTTPException(status_code=403, detail="Licencia inválida")
    return {"status": "valid"}

@app.get("/admin/users")
def get_all_users(current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    users = db.query(database.User).all()
    return [{"email": u.email, "is_admin": u.is_admin} for u in users]

# 👇 Función auxiliar para get_current_user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=email)
    if user is None:
        raise credentials_exception
    return user