from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    username: str = Field(...)
    balance: float = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "balance": 1000.0,
            }
        }




class Transaction(BaseModel):
    username: str = Field(...)
    chat_id: str = Field(...)
    amount: float = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "chat_id": "chat_12345",
                "amount": -5.0,
                "timestamp": "2023-10-10T00:00:00Z"
            }
        }