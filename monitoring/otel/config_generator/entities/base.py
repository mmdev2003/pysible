from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class Component(ABC):
    name: str
    @abstractmethod
    def to_config(self) -> dict:
        pass

    @abstractmethod
    def validate(self, env: str) -> list[str]:
        pass


class Receiver(Component):
    pass


class Processor(Component):
    pass


class Exporter(Component):
    pass


class TelemetryType(Enum):
    TRACES = "traces"
    METRICS = "metrics"
    LOGS = "logs"


class Environment(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


@dataclass
class Endpoint:
    host: str = "127.0.0.1"
    port: int = 4317

    def to_string(self) -> str:
        return f"{self.host}:{self.port}"

    def is_secure(self) -> bool:
        return self.host in ["127.0.0.1", "localhost", "::1"]


@dataclass
class TLSConfig:
    enabled: bool = True
    insecure: bool = False
    cert_file: str = None
    key_file: str = None
    ca_file: str = None

    def to_dict(self) -> dict:
        config = {"insecure": self.insecure}
        if self.cert_file:
            config["cert_file"] = self.cert_file
        if self.key_file:
            config["key_file"] = self.key_file
        if self.ca_file:
            config["ca_file"] = self.ca_file
        return config


@dataclass
class RetryConfig:
    enabled: bool = True
    initial_interval: str = "5s"
    max_interval: str = "30s"
    max_elapsed_time: str = "300s"

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "initial_interval": self.initial_interval,
            "max_interval": self.max_interval,
            "max_elapsed_time": self.max_elapsed_time
        }
