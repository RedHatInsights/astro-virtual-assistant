from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class Session:
    key: str
    user_identity: str


class SessionStorage(ABC):
    def __init__(self):
        pass


    async def put(self, session: Session):
        return await self.store(session)

    async def get(self, session_key: str) -> Session:
        return await self.retrieve(session_key)

    @abstractmethod
    async def store(self, session: Session):
        """
        Stores a session into the storage, replacing if it exists
        """
        pass

    @abstractmethod
    async def retrieve(self, session_key: str) -> Optional[Session]:
        """
        Retrieves the session using the session key
        """
        pass
