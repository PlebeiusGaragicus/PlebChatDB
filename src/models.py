from pydantic import BaseModel, Field
from datetime import datetime



class UserRequest(BaseModel):
    username: str
    balance: int

class TransactionRequest(BaseModel):
    username: str
    chat_id: str
    amount: int

class BalanceRequest(BaseModel):
    username: str
    new_balance: int



class User(BaseModel):
    username: str = Field(...)
    balance: float = Field(...)


class UsernameRequest(BaseModel):
    username: str


class InvoiceRequest(BaseModel):
    username: str
    # tokens_requested: int


class SuccessAction(BaseModel):
    message: str
    tag: str


class UsageDeducation(BaseModel):
    username: str
    thread_id: str
    tokens_used: int

class UsageRequest(BaseModel):
    username: str
    thread_id: str


class UsageRecord(BaseModel):
    username: str = Field(...)
    thread_id: str = Field(...)
    tokens_used: float = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Invoice(BaseModel):
    username: str = Field(...)
    pr: str = Field(...)
    routes: list = Field(default_factory=list)
    status: str = Field(..., pattern="^(pending|settled|archived)$") # Change 'regex' to 'pattern'
    successAction: SuccessAction = Field(...)
    verify: str = Field(...)
    amount: float = Field(...)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
