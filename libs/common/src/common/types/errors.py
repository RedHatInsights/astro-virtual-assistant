from pydantic import BaseModel


class ValidationError(BaseModel):
    message: str
