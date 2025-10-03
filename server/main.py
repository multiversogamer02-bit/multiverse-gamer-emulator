# server/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel
from server import models, database
import os
import bcrypt
import httpx
import hashlib
import hmac

app = FastAPI(title="Multiverse Gamer API")

# Crear tablas al iniciar
models.Base.metadata.create_all(bind=database.engine)

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_inseguro_para_desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# === WEBHOOKS ===

@app.post("/webhooks/mercadopago")
async def mercadopago_webhook(request: Request, db: Session = Depends(get_db)):
    # Validar firma
    signature = request.headers.get("x-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Firma ausente")
    
    try:
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
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validando firma: {str(e)}")
    
    # Procesar evento
    try:
        payload = await request.json()
        data_id = payload.get("data", {}).get("id")
        if not data_id:
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
        if payment_data.get("status") == "approved":
            email = payment_data.get("payer", {}).get("email")
            if email:
                user = get_user(db, email)
                if user:
                    new_license = models.License(
                        user_id=user.id,
                        machine_id="web",
                        plan="mensual",
                        valid_until=datetime.now(timezone.utc) + timedelta(days=30),
                        is_active=True
                    )
                    db.add(new_license)
                    db.commit()
                    return {"status": "licencia_activada"}
        
        return {"status": "evento_procesado"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando webhook: {str(e)}")

@app.post("/webhooks/paypal")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.body()
        headers = dict(request.headers)
        
        client_id = os.getenv("PAYPAL_CLIENT_ID")
        client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise HTTPException(status_code=500, detail="Faltan credenciales de PayPal")
        
        async with httpx.AsyncClient() as client:
            auth_resp = await client.post(
                "https://api.paypal.com/v1/oauth2/token",
                auth=(client_id, client_secret),
                data={"grant_type": "client_credentials"},
                headers={"Accept": "application/json"}
            )
            if auth_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Error autenticando en PayPal")
            
            access_token = auth_resp.json().get("access_token")
            verify_resp = await client.post(
                "https://api.paypal.com/v1/notifications/verify-webhook-signature",
                json={
                    "auth_algo": headers.get("paypal-auth-algo"),
                    "cert_url": headers.get("paypal-cert-url"),
                    "transmission_id": headers.get("paypal-transmission-id"),
                    "transmission_sig": headers.get("paypal-transmission-sig"),
                    "transmission_time": headers.get("paypal-transmission-time"),
                    "webhook_id": os.getenv("PAYPAL_WEBHOOK_ID", ""),
                    "webhook_event": await request.json()
                },
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
        
        verification = verify_resp.json()
        if verification.get("verification_status") != "SUCCESS":
            raise HTTPException(status_code=403, detail="Firma de PayPal inválida")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validando firma de PayPal: {str(e)}")
    
    try:
        payload = await request.json()
        if payload.get("event_type") == "PAYMENT.SALE.COMPLETED":
            # Asumimos que guardaste el email en custom_id al crear el pago
            email = payload.get("resource", {}).get("custom_id")
            if email:
                user = get_user(db, email)
                if user:
                    new_license = models.License(
                        user_id=user.id,
                        machine_id="web",
                        plan="mensual",
                        valid_until=datetime.now(timezone.utc) + timedelta(days=30),
                        is_active=True
                    )
                    db.add(new_license)
                    db.commit()
                    return {"status": "licencia_activada"}
        return {"status": "evento_procesado"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando webhook de PayPal: {str(e)}")