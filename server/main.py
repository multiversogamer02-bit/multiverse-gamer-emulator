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
import hmac
import hashlib
import httpx

# 👇 Validación de variables de entorno al iniciar
def validate_env():
    required = ["SECRET_KEY", "MERCADOPAGO_ACCESS_TOKEN", "MERCADOPAGO_WEBHOOK_SECRET", "DATABASE_URL"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"❌ Variables faltantes: {', '.join(missing)}")
    if not os.getenv("DATABASE_URL", "").startswith("postgresql"):
        print("⚠️  DATABASE_URL no es PostgreSQL. ¿Estás en desarrollo?")
validate_env()

app = FastAPI(title="Multiverse Gamer API")

models.Base.metadata.create_all(bind=database.engine)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
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

class LicenseValidateRequest(BaseModel):
    machine_id: str

class LicenseActivateRequest(BaseModel):
    machine_id: str
    plan: str

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

# ✅ CORREGIDO: función ahora acepta parámetro nombrado 'data'
def create_access_token( dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token( dict):
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

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

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

# ✅ CORREGIDO: definición de función
@app.post("/token")
def login(form_ OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = create_access_token(data={"sub": user.email})  # ✅ Ahora funciona
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
        new_access_token = create_access_token(data={"sub": email})  # ✅ Ahora funciona
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

# 👇 CORREGIDO: recibe JSON
@app.post("/validate-license")
def validate_license(
    request: LicenseValidateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    license = db.query(models.License).filter(
        models.License.machine_id == request.machine_id,
        models.License.user_id == current_user.id,
        models.License.is_active == True
    ).first()
    if not license or datetime.now(timezone.utc) > license.valid_until:
        raise HTTPException(status_code=403, detail="Licencia inválida")
    return {"status": "valid", "expires": license.valid_until.isoformat()}

# 👇 NUEVO: activar licencia con machine_id real
@app.post("/license/activate")
def activate_license(
    request: LicenseActivateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que el usuario tenga una suscripción activa
    subscription = db.query(models.Subscription).filter(
        models.Subscription.user_id == current_user.id,
        models.Subscription.status == "active",
        models.Subscription.end_date > datetime.now(timezone.utc)
    ).first()
    if not subscription:
        raise HTTPException(status_code=403, detail="No tienes suscripción activa")
    
    new_license = models.License(
        user_id=current_user.id,
        machine_id=request.machine_id,
        plan=request.plan,
        valid_until=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True
    )
    db.add(new_license)
    db.commit()
    return {"status": "activated", "expires": new_license.valid_until.isoformat()}

# 👇 NUEVO: cancelar suscripción
@app.post("/subscription/cancel")
def cancel_subscription(
    subscription_id: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que la suscripción pertenece al usuario
    subscription = db.query(models.Subscription).filter(
        models.Subscription.id == subscription_id,
        models.Subscription.user_id == current_user.id
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")

    try:
        from core.payment_manager import cancel_mercadopago_subscription
        success = cancel_mercadopago_subscription(subscription_id)
        if success:
            # Actualizar estado local
            subscription.status = "cancelled"
            db.commit()
            return {"status": "cancelled"}
        else:
            raise HTTPException(status_code=500, detail="No se pudo cancelar en Mercado Pago")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelando: {str(e)}")

# 👇 NUEVO: cerrar sesión
@app.post("/auth/logout")
def logout():
    # FastAPI no tiene sesión en el sentido tradicional, pero puedes invalidar el token
    # En tu cliente, simplemente borra el token local
    return {"msg": "Sesión cerrada"}

# 👇 ELIMINADO: ya no se crea licencia aquí
@app.get("/payment/success")
def payment_success(email: str, plan: str, db: Session = Depends(get_db)):
    user = get_user(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Pago exitoso. Ahora activa tu licencia desde el launcher."}

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

# 👇 WEBHOOK DE MERCADOPAGO PARA SUSCRIPCIONES (solo marca pago aprobado)
@app.post("/webhooks/mercadopago")
async def mercadopago_webhook(request: Request, db: Session = Depends(get_db)):
    signature = request.headers.get("x-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Firma ausente")

    data = await request.body()
    data_str = data.decode("utf-8")

    sig_parts = dict(part.split("=") for part in signature.split(","))
    ts = sig_parts.get("ts")
    v1 = sig_parts.get("v1")

    if not ts or not v1:
        raise HTTPException(status_code=400, detail="Firma mal formada")

    message = f"{ts}{data_str}"
    secret = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Falta MERCADOPAGO_WEBHOOK_SECRET")

    hmac_hash = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hmac_hash, v1):
        raise HTTPException(status_code=403, detail="Firma inválida")
    
    try:
        payload = await request.json()
        action = payload.get("action")
        data_id = payload.get("data", {}).get("id")
        
        if not action or not data_id:
            raise HTTPException(status_code=400, detail="Payload inválido")
        
        mp_access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        if not mp_access_token:
            raise HTTPException(status_code=500, detail="Falta MERCADOPAGO_ACCESS_TOKEN")
        
        async with httpx.AsyncClient() as client:
            payment_resp = await client.get(
                f"https://api.mercadopago.com/v1/payments/{data_id}",
                headers={"Authorization": f"Bearer {mp_access_token}"}
            )
            
        if payment_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="No se pudo obtener el pago")
        
        payment_data = payment_resp.json()
        status = payment_data.get("status")
        email = payment_data.get("payer", {}).get("email")
        plan = "mensual"
        
        if status == "approved" and email:
            user = get_user(db, email)
            if not user:
                # Opcional: crear usuario si no existe
                hashed = get_password_hash(secrets.token_urlsafe(16))
                user = models.User(email=email, hashed_password=hashed)
                db.add(user)
                db.commit()
            
            # Crear suscripción (NO licencia)
            subscription = models.Subscription(
                user_id=user.id,
                plan=plan,
                status="active",
                end_date=datetime.now(timezone.utc) + timedelta(days=30)
            )
            db.add(subscription)
            db.commit()
            return {"status": "suscripcion_activada"}
        
        return {"status": "evento_procesado", "payment_status": status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando webhook: {str(e)}")

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