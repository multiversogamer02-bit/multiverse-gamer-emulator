# server/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel
from server import models, database
from core.email_manager import send_password_reset_email
import os
import bcrypt
import secrets

app = FastAPI(title="Multiverse Gamer API")

models.Base.metadata.create_all(bind=database.engine)

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_inseguro_para_desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30  # Para "Mantener sesión"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class PaymentRequest(BaseModel):
    email: str
    plan: str

class PasswordResetRequest(BaseModel):
    email: str

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

@app.get("/")
def read_root():
    return {"message": "Multiverse Gamer API - Funcionando"}

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user(db, email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed = get_password_hash(password)
    new_user = models.User(email=email, hashed_password=hashed, is_admin=(email == "rodrigoaguirre196@gmail.com"))
    db.add(new_user)
    db.commit()
    return {"msg": "Usuario creado"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/token/refresh")
def refresh_token(refresh_token: str = Form(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = get_user(db, email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        new_access_token = create_access_token(data={"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

@app.post("/auth/forgot-password")
def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    user = get_user(db, email)
    if not user:
        return {"msg": "Si el email es válido, recibirás un enlace."}
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    reset_token = models.PasswordResetToken(email=email, token=token, expires_at=expires_at)
    db.add(reset_token)
    db.commit()
    
    # 👇 Aquí va la URL de restablecimiento
    reset_url = f"https://multiverse-server.onrender.com/auth/reset?token={token}"
    send_password_reset_email(email, token)
    return {"msg": "Email enviado."}

@app.post("/auth/reset-password")
def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    reset_token = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token == token,
        models.PasswordResetToken.expires_at > datetime.now(timezone.utc)
    ).first()
    if not reset_token:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    user = get_user(db, reset_token.email)
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.delete(reset_token)
        db.commit()
    return {"msg": "Contraseña actualizada."}

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
    new_license = models.License(
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
    
# Página de restablecimiento (HTML simple)
@app.get("/auth/reset")
def reset_password_page(token: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restablecer Contraseña - Multiverse Gamer</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #1e1e1e; color: white; text-align: center; padding: 50px; }}
            .container {{ max-width: 400px; margin: 0 auto; background: #2d2d2d; padding: 30px; border-radius: 10px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: none; border-radius: 5px; }}
            button {{ background: #0078d7; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #005a9e; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔒 Restablecer Contraseña</h2>
            <form id="resetForm" method="POST" action="/auth/reset-password">
                <input type="hidden" name="token" value="{token}">
                <input type="password" name="new_password" placeholder="Nueva contraseña" required>
                <button type="submit">Restablecer</button>
            </form>
        </div>
    </body>
    </html>
    """