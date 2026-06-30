"""Data models for the DevOps Monitoring API.

Three layers:
  - Server      : internal dataclass, mutable, holds business logic.
  - ServerIn    : Pydantic schema for incoming POST bodies (validation).
  - ServerOut   : Pydantic schema for outgoing API responses (serialisation).
"""
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


@dataclass
class Server:
    """Internal server representation used throughout the app."""
    id: int
    name: str
    host: str
    port: int
    status: str = "unknown"
    tags: list[str] = field(default_factory=list)

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Schema for registering a new server."""
    name: str
    host: str
    port: int = Field(default=8080, ge=1, le=65535)
    tags: list[str] = []


class ServerOut(BaseModel):
    """Schema returned to the API client."""
    id: int
    name: str
    host: str
    port: int
    status: str
    tags: list[str] = []

    model_config = {"from_attributes": True}
