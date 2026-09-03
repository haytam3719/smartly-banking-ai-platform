from datetime import datetime,timezone
class NoopConversationStore:
    async def touch(self,conversation_id,locale):return None
class RedisConversationStore:
    """Stores only ephemeral routing context, never financial/tool results."""
    def __init__(self,redis,ttl_seconds=1800):self.redis=redis;self.ttl=ttl_seconds
    async def touch(self,conversation_id,locale):
        await self.redis.hset(f'orchestrator:conversation:{conversation_id}',mapping={'locale':locale,'touched_at':datetime.now(timezone.utc).isoformat()});await self.redis.expire(f'orchestrator:conversation:{conversation_id}',self.ttl)
