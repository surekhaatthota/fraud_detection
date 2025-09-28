from fastapi import FastAPI, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, Transaction
from uuid import uuid4
from datetime import datetime
import bcrypt

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Risk scoring logic
def calculate_risk(amount, location, device):
    risk = 0.0
    if amount > 10000:
        risk += 0.4
    if location.lower() not in ["vizag", "hyderabad"]:
        risk += 0.3
    if device.lower() not in ["mobile", "laptop"]:
        risk += 0.3
    return min(round(risk, 2), 1.0)

# Signup route
@app.post("/api/signup")
def signup(username: str = Form(...), password: str = Form(...), name: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return {"status": "error", "message": "Username already exists."}
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(id=str(uuid4()), username=username, password=hashed_pw, name=name)
    db.add(user)
    db.commit()
    return {"status": "success", "message": "Signup successful."}

# Login route
@app.post("/api/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return {"status": "error", "message": "Invalid credentials."}
    return {
        "status": "success",
        "message": "Login successful.",
        "user_id": user.id,
        "username": user.username,
        "name": user.name
    }

# Add transaction route
@app.post("/api/add-transactions")
def add_transaction(
    username: str = Form(...),
    amount: float = Form(...),
    location: str = Form(...),
    device: str = Form(...),
    db: Session = Depends(get_db)
):
    if not username or not location or not device or amount is None:
        return {"status": "error", "message": "Missing required fields."}

    tx = Transaction(
        id=str(uuid4()),
        username=username,
        amount=amount,
        location=location,
        device=device,
        timestamp=datetime.now(),
        risk=calculate_risk(amount, location, device)
    )
    db.add(tx)
    db.commit()
    return {"status": "success", "message": "Transaction added.", "risk": tx.risk}

# View transactions route
@app.get("/api/transactions/{username}")
def get_user_transactions(username: str, db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.username == username).order_by(Transaction.timestamp.desc()).all()
    return {"transactions": [tx.__dict__ for tx in txs]}
