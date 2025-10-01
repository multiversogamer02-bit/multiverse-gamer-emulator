# server/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from server import models, database  # ← Importación correcta
import os

app = FastAPI(title="Multiverse Gamer API")

# Crear tablas al iniciar
models.Base.metadata.create_all(bind=database.engine)

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_inseguro_para_desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class PaymentRequest(BaseModel):
    email: str
    plan: str  # "mensual", "trimestral", "anual"

# Dependencias
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funciones de autenticación
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

# 👇 Definir get_current_user ANTES de los endpoints que lo usan
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
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Multiverse Gamer API - Funcionando"}

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
def validate_license(machine_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    license = db.query(models.License).filter(
        models.License.machine_id == machine_id,
        models.License.user_id == current_user.id,
        models.License.is_active == True
    ).first()
    if not license or datetime.now(timezone.utc) > license.valid_until:
        raise HTTPException(status_code=403, detail="Licencia inválida")
    return {"status": "valid", "expires": license.valid_until.isoformat()}

@app.get("/payment/success")
def payment_success(email: str, plan: str, db: Session = Depends(get_db)):
    user = get_user(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    new_license = database.License(
        user_id=user.id,
        machine_id="web",
        plan=plan,
        valid_until=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True
    )
    db.add(new_license)
    db.commit()
    return {"message": "Pago exitoso. Licencia activada."}

@app.get("/payment/failure")
def payment_failure():
    return {"message": "Pago cancelado o fallido."}

@app.get("/payment/pending")
def payment_pending():
    return {"message": "Pago pendiente de confirmación."}

@app.post("/payment/mercadopago")
def mercadopago_payment(payment: PaymentRequest, db: Session = Depends(get_db)):
    from core.payment_manager import create_mercadopago_payment
    try:
        payment_url = create_mercadopago_payment(payment.email, payment.plan)
        return {"payment_url": payment_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Mercado Pago: {str(e)}")

@app.post("/payment/paypal")
def paypal_payment(payment: PaymentRequest, db: Session = Depends(get_db)):
    from core.payment_manager import create_paypal_payment
    try:
        payment_url = create_paypal_payment(payment.email, payment.plan)
        return {"payment_url": payment_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en PayPal: {str(e)}")

@app.get("/admin/users")
def get_all_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    users = db.query(models.User).all()
    return [{
        "email": u.email,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "is_admin": u.is_admin
    } for u in users]