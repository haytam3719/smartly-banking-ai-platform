from __future__ import annotations
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

CAPABILITY = "card.info.read"

class AgentRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    request_id:str=Field(min_length=1,max_length=128)
    correlation_id:str=Field(min_length=1,max_length=128)
    conversation_id:str=Field(min_length=1,max_length=128)
    subject:str=Field(min_length=1,max_length=256)
    customer_id:str=Field(min_length=1,max_length=128)
    capability:str=Field(min_length=1,max_length=128)
    arguments:dict[str,Any]
    locale:str=Field(pattern=r"^[a-z]{2,3}(?:-[A-Z]{2})?$")

class ErrorResponse(BaseModel):
    code:str;message:str;request_id:str;retryable:bool

class AgentResponse(BaseModel):
    success:bool;capability:str;data:Any;error:ErrorResponse|None;metadata:dict[str,Any];latency_ms:int=Field(ge=0)

class CardInfo(BaseModel):
    card_type:str
    status:str
    expiration_date:str=Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    payment_limit:Decimal=Field(ge=0)
    amount_used:Decimal=Field(ge=0)
    available_limit:Decimal=Field(ge=0)
    currency:str=Field(pattern=r"^[A-Z]{3}$")

class CallContext(BaseModel):
    request_id:str;correlation_id:str;conversation_id:str

