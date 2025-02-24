from pydantic import BaseModel
from typing import Optional, List, Union


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


class TalkResponseItem(BaseModel):
    # parent class for response types
    pass


class TalkResponseOption(BaseModel):
    label: str
    input: Optional[TalkInput] = None


class TalkResponseText(TalkResponseItem):
    text: Optional[str] = None
    options: Optional[List[TalkResponseOption]] = None


class TalkResponseCommandData(BaseModel):
    type: str
    args: Optional[List[str]] = None


class TalkResponseCommand(TalkResponseItem):
    command: TalkResponseCommandData


response_item_types = Union[TalkResponseText, TalkResponseCommand]


class TalkResponse(BaseModel):
    response: Optional[List[response_item_types]] = None
    session_id: str
