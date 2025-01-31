from pydantic import BaseModel
from typing import Optional, List


class TalkRequestInputIntents(BaseModel):
    intent: str
    confidence: Optional[float] = None
    skill: Optional[str] = None


class TalkRequestInputEntities(BaseModel):
    entity: str
    location: Optional[List[int]] = []
    value: str
    confidence: Optional[float] = None
    groups: Optional[dict] = {}
    interpretation: Optional[dict] = {}
    alternatives: Optional[dict] = {}
    role: Optional[dict] = {}
    skill: Optional[str] = {}


class TalkRequestInputAttachments(BaseModel):
    url: str
    media_type: Optional[str] = None


class TalkRequestInputAnalytics(BaseModel):
    browser: Optional[str] = None
    device: Optional[str] = None
    page_url: Optional[str] = None


class TalkInput(BaseModel):
    message_type: Optional[str] = None
    text: Optional[str] = None
    intents: Optional[List[TalkRequestInputIntents]] = None
    entities: Optional[List[TalkRequestInputEntities]] = None
    suggestion_id: Optional[str] = None
    attachments: Optional[TalkRequestInputAttachments] = None
    analytics: Optional[TalkRequestInputAnalytics] = None
    options: Optional[dict] = None


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


class TalkRequestError(BaseModel):
    message: str


def watson_response_formatter(session_id: str, response: dict) -> TalkResponse:
    watson_generic = response["output"]["generic"]
    normalized_watson_response = []

    for generic in watson_generic:
        if generic["response_type"] == "text":
            normalized_watson_response.append({"text": generic["text"]})

        if generic["response_type"] == "option":
            options = []
            for option in generic["options"]:
                options.append(
                    {"label": option["label"], "input": option["value"].get("input")}
                )
            normalized_watson_response.append({"options": options})

        if generic["response_type"] == "suggestion":
            options = []
            for suggestion in generic["suggestions"]:
                options.append(
                    {
                        "label": suggestion["label"],
                        "input": suggestion["value"].get("input"),
                    }
                )
            normalized_watson_response.append(
                {"text": generic["title"], "options": options}
            )

    normalized_response = {
        "session_id": session_id,
        "response": normalized_watson_response,
    }

    return TalkResponse(**normalized_response)
