import time
import httpx
from orchestrator.models import AgentResult,Decision,RagResult,Resolution

class IntegrationError(RuntimeError):
    def __init__(self,code:str,retryable:bool=True):self.code=code;self.retryable=retryable
class HttpRegistryClient:
    def __init__(self,client,base_url,ttl=30):self.client=client;self.base=base_url.rstrip('/');self.ttl=ttl;self.cache={}
    async def resolve(self,capability,headers):
        cached=self.cache.get(capability)
        if cached and cached[0]>time.monotonic():return cached[1]
        try:r=await self.client.get(f'{self.base}/internal/v1/capabilities/{capability}',headers=headers)
        except httpx.HTTPError as exc:raise IntegrationError('REGISTRY_UNAVAILABLE') from exc
        if r.status_code==404:raise IntegrationError('UNKNOWN_CAPABILITY',False)
        if r.status_code>=400:raise IntegrationError('REGISTRY_UNAVAILABLE')
        value=Resolution.model_validate(r.json());self.cache[capability]=(time.monotonic()+self.ttl,value);return value
    async def health(self):
        try:return (await self.client.get(f'{self.base}/internal/v1/health/agents')).status_code<500
        except httpx.HTTPError:return False
class HttpPolicyClient:
    def __init__(self,client,base_url):self.client=client;self.base=base_url.rstrip('/')
    async def authorize(self,principal,capability,customer_id,resource,headers):
        body={'subject':{'id':principal.subject_id,'roles':principal.roles,'scopes':principal.scopes},'customer_id':customer_id,'capability':capability,'resource':resource,'context':{'channel':principal.channel}}
        trusted={**headers,'X-Authenticated-Subject-Id':principal.subject_id}
        if principal.customer_id:trusted['X-Authenticated-Customer-Id']=principal.customer_id
        try:r=await self.client.post(f'{self.base}/internal/v1/authorize',json=body,headers=trusted)
        except httpx.HTTPError as exc:raise IntegrationError('POLICY_UNAVAILABLE') from exc
        if r.status_code>=400:raise IntegrationError('POLICY_UNAVAILABLE')
        return Decision.model_validate(r.json())
    async def health(self):
        try:return (await self.client.get(f'{self.base}/health')).status_code<500
        except httpx.HTTPError:return False
class HttpAgentClient:
    def __init__(self,client):self.client=client
    async def execute(self,resolution,payload,headers,retry=True):
        attempts=2 if retry else 1
        for attempt in range(attempts):
            try:r=await self.client.post(f'{resolution.base_url}/internal/v1/capabilities/{resolution.capability.value}',json=payload,headers=headers,timeout=resolution.timeout_ms/1000)
            except httpx.TimeoutException as exc:
                if attempt+1==attempts:raise IntegrationError('AGENT_TIMEOUT') from exc
                continue
            except httpx.HTTPError as exc:raise IntegrationError('AGENT_UNAVAILABLE') from exc
            if r.status_code>=500 and attempt+1<attempts:continue
            if r.status_code>=400:raise IntegrationError('AGENT_ERROR',r.status_code>=500)
            return AgentResult.model_validate(r.json())
        raise IntegrationError('AGENT_UNAVAILABLE')
class HttpKnowledgeClient:
    def __init__(self,client):self.client=client
    async def search(self,resolution,query,locale,filters,headers):
        try:r=await self.client.post(f'{resolution.base_url}/internal/v1/search',json={'query':query,'top_k':4,'locale':locale,'filters':filters,'score_threshold':.15},headers=headers,timeout=resolution.timeout_ms/1000)
        except httpx.HTTPError as exc:raise IntegrationError('KNOWLEDGE_UNAVAILABLE') from exc
        if r.status_code>=400:raise IntegrationError('KNOWLEDGE_UNAVAILABLE')
        return [RagResult.model_validate(x) for x in r.json()['results']]
