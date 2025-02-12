from pydantic import BaseModel
from typing import Optional, List


class TalkRequestInputIntents(BaseModel):
    intent: str
    confidence: Optional[float] = None


class TalkInput(BaseModel):
    text: Optional[str] = None
    intents: Optional[List[TalkRequestInputIntents]] = None
    suggestion_id: Optional[str] = None


class TalkRequest(BaseModel):
    session_id: Optional[str] = None
    input: TalkInput


class TalkResponseOptionsItems(BaseModel):
    label: str
    input: Optional[TalkInput] = None


class TalkResponseListItems(BaseModel):
    text: Optional[str] = None
    options: Optional[List[TalkResponseOptionsItems]] = None


class TalkResponse(BaseModel):
    response: Optional[List[TalkResponseListItems]] = None
    session_id: str
