from enum import StrEnum
from typing import Any,Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator

class Capability(StrEnum):
    ACCOUNT_BALANCE_READ="account.balance.read";ACCOUNT_TRANSACTIONS_READ="account.transactions.read";CARD_INFO_READ="card.info.read";TRANSFER_STATUS_READ="transfer.status.read";CUSTOMER_INFO_READ="customer.info.read";KNOWLEDGE_SEARCH="knowledge.search";ACCOUNT_OPENING_START="account.opening.start";ACCOUNT_OPENING_STATUS="account.opening.status"
class RoutingMode(StrEnum):
    DIRECT = "DIRECT"
    RAG_ONLY = "RAG_ONLY"
    TOOLS_ONLY = "TOOLS_ONLY"
    HYBRID = "HYBRID"
    WORKFLOW = "WORKFLOW"
    CLARIFY = "CLARIFY"
    UNSUPPORTED = "UNSUPPORTED"
class Intent(StrEnum):
    DIRECT="DIRECT";BALANCE="BALANCE";TRANSACTIONS="TRANSACTIONS";CARD_INFO="CARD_INFO";CUSTOMER_INFO="CUSTOMER_INFO";TRANSFER_STATUS="TRANSFER_STATUS";TRANSFER_EXPLANATION="TRANSFER_EXPLANATION";BANKING_KNOWLEDGE="BANKING_KNOWLEDGE";ACCOUNT_OPENING="ACCOUNT_OPENING";ACCOUNT_OPENING_STATUS="ACCOUNT_OPENING_STATUS";UNSUPPORTED="UNSUPPORTED"
class IntentResult(BaseModel):
    model_config=ConfigDict(extra="forbid")
    intent:Intent
    transfer_id:str|None=None
    opening_id:str|None=None
    account_type:str|None=None
    currency:str|None=None
class PlannedAction(BaseModel):
    model_config=ConfigDict(extra="forbid")
    capability:Capability
    arguments:dict[str,Any]=Field(default_factory=dict)
class RoutingPlan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    mode:RoutingMode
    actions:list[PlannedAction]=Field(default_factory=list,max_length=6)
    clarification:str|None=None
    @model_validator(mode="after")
    def coherent(self):
        capabilities=[a.capability for a in self.actions]
        if len(capabilities)!=len(set(capabilities)):raise ValueError("duplicate capabilities")
        if self.mode in {
            RoutingMode.CLARIFY,
            RoutingMode.UNSUPPORTED,
            RoutingMode.DIRECT,
        } and self.actions:
            raise ValueError("terminal route cannot contain actions")

        if self.mode not in {
            RoutingMode.CLARIFY,
            RoutingMode.UNSUPPORTED,
            RoutingMode.DIRECT,
        } and not self.actions:raise ValueError("action required")
        if self.mode==RoutingMode.RAG_ONLY and capabilities!=[Capability.KNOWLEDGE_SEARCH]:raise ValueError("RAG_ONLY permits only knowledge.search")
        if self.mode==RoutingMode.TOOLS_ONLY and Capability.KNOWLEDGE_SEARCH in capabilities:raise ValueError("TOOLS_ONLY cannot search knowledge")
        if self.mode==RoutingMode.HYBRID and (Capability.KNOWLEDGE_SEARCH not in capabilities or len(capabilities)<2):raise ValueError("HYBRID requires tool and RAG")
        if self.mode==RoutingMode.WORKFLOW and any(x not in {Capability.ACCOUNT_OPENING_START,Capability.ACCOUNT_OPENING_STATUS} for x in capabilities):raise ValueError("WORKFLOW contains invalid capability")
        return self
class ChatRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    customer_id:str=Field(min_length=1,max_length=128);message:str=Field(min_length=1,max_length=8000);conversation_id:str|None=Field(default=None,min_length=1,max_length=128);locale:str=Field(default="fr-FR",pattern=r"^[a-z]{2,3}(?:-[A-Z]{2})?$")
class Evidence(BaseModel):
    model_config=ConfigDict(extra="forbid")
    type:Literal["TOOL","RAG"];source:str;content:str|None=None;data:Any=None;confidence:float|None=Field(default=None,ge=0,le=1);metadata:dict[str,Any]=Field(default_factory=dict)
class ChatResponse(BaseModel):
    answer:str;source:str;sources:list[Evidence];conversation_id:str;request_id:str
class Principal(BaseModel):
    subject_id:str;customer_id:str|None;roles:list[str]=Field(default_factory=lambda:["CUSTOMER"]);scopes:list[str]=Field(default_factory=list);channel:Literal["MOBILE","WEB","INTERNAL"]="INTERNAL"
class Resolution(BaseModel):
    capability:Capability;agent_id:str;base_url:str;version:str;timeout_ms:int
class Decision(BaseModel):
    allowed:bool;decision_id:str;reason_code:str;obligations:list[dict[str,Any]]=Field(default_factory=list)
class AgentResult(BaseModel):
    success:bool;capability:Capability;data:Any=None;error:dict[str,Any]|None=None;metadata:dict[str,Any]=Field(default_factory=dict);latency_ms:int=0
class RagResult(BaseModel):
    content:str;document_id:str;document_type:str;score:float;metadata:dict[str,Any]
class AnswerDraft(BaseModel):
    model_config=ConfigDict(extra="forbid")
    answer:str=Field(min_length=1,max_length=4000)
