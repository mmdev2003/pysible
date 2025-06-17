from dataclasses import dataclass

from .base import Endpoint

@dataclass
class Extension:
    name: str
    endpoint: Endpoint

    def to_config(self) -> dict:
        return {"endpoint": self.endpoint.to_string()}