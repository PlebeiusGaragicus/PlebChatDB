from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson.objectid import ObjectId

from server.models import User, Transaction
from server.database import db, connect_to_mongo, close_mongo_connection

class UserRequest(BaseModel):
    username: str
    balance: float

class TransactionRequest(BaseModel):
    chat_id: str
    amount: float

def transaction_helper(transaction) -> dict:
    """Helper function to convert MongoDB transaction to JSON-compatible format."""
    return {
        "id": str(transaction["_id"]),
        "username": transaction["username"],
        "chat_id": transaction["chat_id"],
        "amount": transaction["amount"],
        "timestamp": transaction["timestamp"]
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Optional CORS middleware if you need to allow cross-origin requests
origins = [
    "http://localhost",
    "http://localhost:8501",
    # Add the origins you need
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/")
async def create_user(user_request: UserRequest):
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": user_request.username})
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(**user_request.dict())
    await user_collection.insert_one(user.dict())
    return user

@app.get("/users/", response_model=List[User])
async def get_all_users():
    user_collection = db.db.get_collection("users")
    users = await user_collection.find().to_list(length=None)
    return users

@app.get("/users/{username}/balance/")
async def get_balance(username: str):
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "balance": user["balance"]}

@app.put("/users/{username}/balance/deduct")
async def deduct_balance(username: str, transaction_request: TransactionRequest):
    user_collection = db.db.get_collection("users")
    transactions_collection = db.db.get_collection("transactions")

    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_balance = user["balance"] + transaction_request.amount
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    user["balance"] = new_balance
    await user_collection.update_one({"username": username}, {"$set": {"balance": new_balance}})

    transaction = Transaction(username=username, chat_id=transaction_request.chat_id, amount=transaction_request.amount)
    await transactions_collection.insert_one(transaction.dict())

    return {"username": username, "balance": new_balance}

@app.get("/users/{username}/transactions/")
async def get_transactions(username: str):
    transactions_collection = db.db.get_collection("transactions")
    transactions = await transactions_collection.find({"username": username}).to_list(length=None)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")
    # Convert MongoDB transactions to JSON-compatible format
    transactions = [transaction_helper(transaction) for transaction in transactions]
    return transactions
