from uuid import uuid4
from opentelemetry import trace
from orchestrator.models import ChatRequest,ChatResponse,Principal
tracer=trace.get_tracer(__name__)
class ChatService:
    def __init__(self,graph):self.graph=graph
    async def chat(self,request:ChatRequest,principal:Principal,request_id:str|None=None,correlation_id:str|None=None)->ChatResponse:
        rid=request_id or str(uuid4());cid=correlation_id or rid;conversation=request.conversation_id or str(uuid4())
        if principal.customer_id is not None and principal.customer_id!=request.customer_id:
            return ChatResponse(answer="Je ne peux pas accéder à ce contexte client.",source="none",sources=[],conversation_id=conversation,request_id=rid)
        with tracer.start_as_current_span('chat.request'):
            state=await self.graph.invoke({'request':request,'principal':principal,'request_id':rid,'correlation_id':cid,'conversation_id':conversation})
        return state['response']
