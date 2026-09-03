import logging,os,sys
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from pythonjsonlogger.json import JsonFormatter
from redis.asyncio import from_url
from orchestrator.api import router
from orchestrator.audit import StructuredLogAuditPublisher
from orchestrator.clients import HttpAgentClient,HttpKnowledgeClient,HttpPolicyClient,HttpRegistryClient
from orchestrator.conversation import NoopConversationStore,RedisConversationStore
from orchestrator.graph import OrchestrationGraph
from orchestrator.llm import DirectAnswerGenerator,GroundedAnswerGenerator,HeuristicRouter,OpenAICompatibleDirectAnswer,OpenAICompatibleGroundedAnswer,OpenAICompatibleStructuredRouter
from orchestrator.service import ChatService
from orchestrator.telemetry import configure_tracing
handler=logging.StreamHandler(sys.stdout);handler.setFormatter(JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'));logging.getLogger().handlers=[handler];logging.getLogger().setLevel(logging.INFO);configure_tracing();HTTPXClientInstrumentor().instrument()
@asynccontextmanager
async def lifespan(app:FastAPI):
    client=httpx.AsyncClient(timeout=httpx.Timeout(connect=3, read=30, write=10, pool=5));registry=HttpRegistryClient(client,os.getenv('AGENT_REGISTRY_URL','http://agent-registry:8080'));policy=HttpPolicyClient(client,os.getenv('POLICY_ENGINE_URL','http://policy-engine:8080'));mode=os.getenv('LLM_PROVIDER','heuristic')
    if mode=='openai-compatible':router_impl=OpenAICompatibleStructuredRouter(client,os.environ['LLM_BASE_URL'],os.environ['LLM_API_KEY'],os.getenv('LLM_MODEL','gpt-4.1-mini'));answerer=OpenAICompatibleGroundedAnswer(client,os.environ['LLM_BASE_URL'],os.environ['LLM_API_KEY'],os.getenv('LLM_MODEL','gpt-4.1-mini'));direct_answerer=OpenAICompatibleDirectAnswer(client,os.environ['LLM_BASE_URL'],os.environ['LLM_API_KEY'],os.getenv('LLM_MODEL','gpt-4.1-mini'))
    else:router_impl=HeuristicRouter();answerer=GroundedAnswerGenerator();direct_answerer=DirectAnswerGenerator()
    redis_client=from_url(os.environ['REDIS_URL'],decode_responses=True) if os.getenv('REDIS_URL') else None;conversations=RedisConversationStore(redis_client) if redis_client else NoopConversationStore()
    graph=OrchestrationGraph(router_impl,answerer,direct_answerer,registry,policy,HttpAgentClient(client),HttpKnowledgeClient(client),StructuredLogAuditPublisher(),conversations);app.state.chat_service=ChatService(graph);app.state.registry=registry;app.state.policy=policy
    try:yield
    finally:
        await client.aclose()
        if redis_client:await redis_client.aclose()
app=FastAPI(title='Smartly AI Orchestrator',version='1.0.0',description='Policy-gated LangGraph orchestration; LLMs cannot execute banking APIs.',lifespan=lifespan);app.include_router(router);FastAPIInstrumentor.instrument_app(app,excluded_urls='/health/live,/health/ready')
