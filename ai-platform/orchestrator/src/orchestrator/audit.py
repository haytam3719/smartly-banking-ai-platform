import json,logging
from datetime import datetime,timezone
from uuid import uuid4
logger=logging.getLogger(__name__)
class StructuredLogAuditPublisher:
    async def publish(self,event_type,payload,context):
        event={'event_id':str(uuid4()),'event_type':event_type,'occurred_at':datetime.now(timezone.utc).isoformat(),'trace_id':context.get('trace_id',''),'correlation_id':context['correlation_id'],'conversation_id':context.get('conversation_id'),'service':'ai-orchestrator','payload':payload}
        logger.info('audit_event',extra={'event':event})
class KafkaCompatibleAuditPublisher:
    """Adapter boundary for aiokafka/confluent producers; value is already privacy-minimized."""
    def __init__(self,producer,topic='smartly.ai.audit'):self.producer=producer;self.topic=topic
    async def publish(self,event_type,payload,context):
        event={'event_id':str(uuid4()),'event_type':event_type,'occurred_at':datetime.now(timezone.utc).isoformat(),'trace_id':context.get('trace_id',''),'correlation_id':context['correlation_id'],'conversation_id':context.get('conversation_id'),'service':'ai-orchestrator','payload':payload}
        await self.producer.send_and_wait(self.topic,json.dumps(event).encode())
