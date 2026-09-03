import os
from fastapi import FastAPI
from httpx import ASGITransport,AsyncClient
from orchestrator.api import router
class Chat:
    async def chat(self,body,principal,request_id,correlation_id):
        from orchestrator.models import ChatResponse
        return ChatResponse(answer='ok',source='none',sources=[],conversation_id=body.conversation_id or 'generated',request_id=request_id or 'generated')
async def test_both_chat_paths_and_cross_customer(monkeypatch):
    monkeypatch.setenv('DEV_AUTH_MODE','false');app=FastAPI();app.include_router(router);app.state.chat_service=Chat()
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        headers={'X-Authenticated-Subject-Id':'user-1','X-Authenticated-Customer-Id':'C1024','X-Scopes':'account:read'};body={'customer_id':'C1024','message':'solde','locale':'fr-FR'}
        assert (await client.post('/chat',json=body,headers=headers)).status_code==200;assert (await client.post('/api/v1/chat',json=body,headers=headers)).status_code==200
        denied=await client.post('/chat',json=body,headers={**headers,'X-Authenticated-Customer-Id':'C2048'});assert denied.status_code==404
        malformed=await client.post('/chat',json={'customer_id':'','message':''},headers=headers);assert malformed.status_code==422
