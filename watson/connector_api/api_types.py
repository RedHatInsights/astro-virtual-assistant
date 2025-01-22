from pydantic import BaseModel
from typing import Optional


class TalkRequestMetadata(BaseModel):
    session_id: Optional[str] = None
    # account: str
    # org_id: str

class TalkRequest(BaseModel):
    message: str
    metadata: TalkRequestMetadata
