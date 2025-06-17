from .base import TelemetryType

from dataclasses import dataclass, field



@dataclass
class Pipeline:
    name: str
    telemetry_type: TelemetryType
    receivers: list[str] = field(default_factory=list)
    processors: list[str] = field(default_factory=list)
    exporters: list[str] = field(default_factory=list)
    enabled: bool = True

    def to_config(self) -> dict:
        config = {"receivers": self.receivers}
        if self.processors:
            config["processors"] = self.processors
        if self.exporters:
            config["exporters"] = self.exporters
        return config

    def validate(self) -> list[str]:
        warnings = []
        if not self.receivers:
            warnings.append(f"⚠️ Pipeline {self.name}: Нет receivers")
        if not self.exporters:
            warnings.append(f"⚠️ Pipeline {self.name}: Нет exporters")

        if self.processors and "memory_limiter" in self.processors:
            if self.processors[0] != "memory_limiter":
                warnings.append(f"⚠️ Pipeline {self.name}: memory_limiter должен быть первым processor")

        has_batch = any("batch" in proc for proc in self.processors)
        if not has_batch:
            warnings.append(f"⚠️ Pipeline {self.name}: Отсутствует batch processor, снижена производительность")

        return warnings