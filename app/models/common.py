from pydantic import BaseModel


class RGBA(BaseModel):
    """RGBA color model with red, green, blue, and alpha channels."""

    r: float
    g: float
    b: float
    a: float


class Identified(BaseModel):
    """A model with an identifier."""

    id: str
