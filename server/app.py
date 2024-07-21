import os
import logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    }
}

import logging.config

# Load the logging configuration
logging.config.dictConfig(logging_config)

# Get the root logger
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List

from server.models import User, Transaction, Invoice, UsernameRequest
from server.database import db, connect_to_mongo, close_mongo_connection
import server.invoice as invoice_utils


class UserRequest(BaseModel):
    username: str
    balance: int

class TransactionRequest(BaseModel):
    username: str
    chat_id: str
    amount: int

class IncreaseBalanceRequest(BaseModel):
    username: str
    amount: int

def transaction_helper(transaction) -> dict:
    return {
        "id": str(transaction["_id"]),
        "username": transaction["username"],
        "chat_id": transaction["chat_id"],
        "amount": transaction["amount"],
        "timestamp": transaction["timestamp"]
    }

def invoice_helper(invoice) -> dict:
    return {
        "id": str(invoice["_id"]),
        "username": invoice["username"],
        "status": invoice["status"],
        "amount": invoice["amount"],
        "issued_at": invoice["issued_at"]
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to MongoDB...")
    await connect_to_mongo()
    yield
    logger.info("Closing MongoDB connection...")
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5522",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response



@app.get("/balance/")
async def get_balance(request: Request):
    logger.debug("get_balance endpoint called")
    logger.debug(f"Request: {request}")
    data = await request.json()
    username = data['username']
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "balance": user["balance"]}

@app.get("/invoice/")
async def get_invoice(request: UsernameRequest):
    logger.debug("get_invoice endpoint called")
    logger.debug(f"Request: {request}")
    username = request.username
    invoices_collection = db.db.get_collection("invoices")
    user_collection = db.db.get_collection("users")

    pending_invoice = await invoices_collection.find_one({"username": username, "status": "pending"})
    print("Pending invoice:", pending_invoice)

    if pending_invoice:
        is_paid = invoice_utils.check_for_payment(pending_invoice)
        if is_paid:
            user = await user_collection.find_one({"username": username})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            new_balance = user["balance"] + pending_invoice["amount"]
            async with await db.client.start_session() as s:
                async with s.start_transaction():
                    await user_collection.update_one(
                        {"username": username}, {"$set": {"balance": new_balance}}, session=s
                    )
                    await invoices_collection.update_one(
                        {"_id": pending_invoice["_id"]}, {"$set": {"status": "archived"}}, session=s
                    )
            return {"message": "Invoice paid, balance updated"}
        else:
            return invoice_helper(pending_invoice)

    print("No pending invoice found")
    new_invoice_details = invoice_utils.create_invoice(amount=100)
    if 'error' in new_invoice_details:
        raise HTTPException(status_code=500, detail=new_invoice_details['error'])
    
    new_invoice = Invoice(username=username, status="pending", amount=new_invoice_details['amount'])
    insert_result = await invoices_collection.insert_one(new_invoice.dict())
    new_invoice_id = insert_result.inserted_id
    new_invoice_dict = new_invoice.dict()
    new_invoice_dict['_id'] = new_invoice_id

    return invoice_helper(new_invoice_dict)





@app.put("/tx/")
async def deduct_balance(transaction_request: TransactionRequest):
    logger.debug("deduct_balance endpoint called")
    logger.debug(f"Request: {transaction_request}")
    username = transaction_request.username
    user_collection = db.db.get_collection("users")
    transactions_collection = db.db.get_collection("transactions")

    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_balance = user["balance"] + transaction_request.amount
    # if new_balance < 0:
    #     raise HTTPException(status_code=400, detail="Insufficient funds")

    user["balance"] = new_balance
    await user_collection.update_one({"username": username}, {"$set": {"balance": new_balance}})

    transaction = Transaction(username=username, chat_id=transaction_request.chat_id, amount=transaction_request.amount)
    await transactions_collection.insert_one(transaction.dict())

    return {"username": username, "balance": new_balance}


@app.get("/usage/")
async def get_transactions(request: Request):
    logger.debug("get_transactions endpoint called")
    logger.debug(f"Request: {request}")
    data = await request.json()
    username = data['username']
    transactions_collection = db.db.get_collection("transactions")
    transactions = await transactions_collection.find({"username": username}).to_list(length=None)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")
    transactions = [transaction_helper(transaction) for transaction in transactions]
    return transactions


@app.post("/invoices/")
async def get_invoices(request: UsernameRequest):
    username = request.username
    invoices_collection = db.db.get_collection("invoices")
    invoices = await invoices_collection.find({"username": username}).to_list(length=None)
    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found for this user")
    
    invoices = [invoice_helper(invoice) for invoice in invoices]
    return invoices

















############################################################
#TODO: ADMIN TESTING ENDPOINTS!
############################################################






@app.get("/admin/users/", response_model=List[User])
async def get_all_users():
    user_collection = db.db.get_collection("users")
    users = await user_collection.find().to_list(length=None)
    return users


@app.post("/admin/users/")
async def create_user(user_request: UserRequest):
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": user_request.username})
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(**user_request.dict())
    await user_collection.insert_one(user.dict())
    return user


@app.delete("/admin/users/")
async def delete_user(request: UsernameRequest):
    username = request.username
    user_collection = db.db.get_collection("users")
    result = await user_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {username} deleted successfully"}








@app.put("/admin/users/balance/increase")
async def increase_balance(request: IncreaseBalanceRequest):
    username = request.username
    amount = request.amount
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_balance = user["balance"] + amount

    await user_collection.update_one({"username": username}, {"$set": {"balance": new_balance}})
    
    return {"username": username, "new_balance": new_balance}

@app.post("/admin/cleanup/pending/")
async def cleanup_pending_invoices(request: UsernameRequest):
    username = request.username
    invoices_collection = db.db.get_collection("invoices")
    result = await invoices_collection.delete_many({"username": username, "status": "pending"})
    if result.deleted_count > 0:
        return {"message": f"Deleted {result.deleted_count} pending invoices for user {username}"}
    else:
        raise HTTPException(status_code=404, detail="No pending invoices found for the user")

@app.post("/admin/cleanup/archived/")
async def cleanup_archived_invoices(request: UsernameRequest):
    username = request.username
    invoices_collection = db.db.get_collection("invoices")
    result = await invoices_collection.delete_many({"username": username, "status": "archived"})
    if result.deleted_count > 0:
        return {"message": f"Deleted {result.deleted_count} archived invoices for user {username}"}
    else:
        raise HTTPException(status_code=404, detail="No archived invoices found for the user")







@app.get("/health")
def read_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append(route.path)
    return {"routes": routes}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5101)
