from redis.asyncio import StrictRedis
from typing import Optional

from common.config import app
from . import Session, SessionStorage

class RedisSessionStorage(SessionStorage):
    """
    Redis session storage - Used to store and retrieve the session_id/identity header pair
    """

    def __init__(self):
        super().__init__()
        self.redis_client = StrictRedis(
            host=app.redis_hostname,
            port=app.redis_port,
            username=app.redis_username,
            password=app.redis_password,
            decode_responses=True,
        )

    async def retrieve(self, session_key: str) -> Optional[Session]:    
        """Read the identity header from Redis using the session_id"""
        value = await self.redis_client.get(session_key)
        if value:
            return value
        else:
            return None

    async def store(self, session: Session):
        """Write the session_id/identity header pair to Redis."""
        await self.redis_client.set(session.key, session.value)

