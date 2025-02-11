import json

from redis.asyncio import Redis
from typing import Optional

from . import Session, SessionStorage

class RedisSessionStorage(SessionStorage):
    """
    Redis session storage - Used to store and retrieve the session_id/identity header pair
    """

    def __init__(self, redis_client: Redis):
        super().__init__()
        self.redis_client = redis_client

    async def retrieve(self, session_key: str) -> Optional[Session]:    
        """Read the identity header from Redis using the session_id"""
        value = await self.redis_client.get(session_key)
        if value:
            return Session(**json.loads(value))
        else:
            return None

    async def store(self, session: Session):
        """Write the session_id/identity header pair to Redis."""
        await self.redis_client.set(session.key, json.dumps(vars(session)))
