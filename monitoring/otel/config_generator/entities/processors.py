from .base import TelemetryType, Processor

class MemoryLimiterProcessor(Processor):
    def __init__(self, name: str = "memory_limiter"):
        self.name = name
        self.type = "memory_limiter"
        self.check_interval = "1s"
        self.limit_mib = 512
        self.spike_limit_mib = 128

    def to_config(self) -> dict:
        return {
            "check_interval": self.check_interval,
            "limit_mib": self.limit_mib,
            "spike_limit_mib": self.spike_limit_mib
        }

    def validate(self, env: str) -> list[str]:
        warnings = []
        if self.spike_limit_mib > self.limit_mib * 0.5:
            warnings.append(f"⚠️ {self.name}: spike_limit_mib превышает 50% от limit_mib")
        return warnings


class BatchProcessor(Processor):
    def __init__(self, name: str, telemetry_type: TelemetryType):
        self.name = name
        self.type = "batch"
        self.telemetry_type = telemetry_type

        defaults = {
            TelemetryType.TRACES: (256, 512, "1s"),
            TelemetryType.METRICS: (1024, 2048, "5s"),
            TelemetryType.LOGS: (512, 1024, "1s")
        }

        self.send_batch_size, self.send_batch_max_size, self.timeout = defaults[telemetry_type]

    def to_config(self) -> dict:
        return {
            "send_batch_size": self.send_batch_size,
            "send_batch_max_size": self.send_batch_max_size,
            "timeout": self.timeout
        }

    def validate(self, env: str) -> list[str]:
        warnings = []
        if self.send_batch_max_size < self.send_batch_size:
            warnings.append(f"⚠️ {self.name}: send_batch_max_size меньше send_batch_size")
        return warnings


class AttributesProcessor(Processor):
    def __init__(self, name: str = "attributes"):
        self.name = name
        self.type = "attributes"
        self.actions: list[dict] = []

    def add_action(self, action: str, key: str, value: str = None) -> 'AttributesProcessor':
        action_config = {"action": action, "key": key}
        if value:
            action_config["value"] = value
        self.actions.append(action_config)
        return self

    def to_config(self) -> dict:
        return {"actions": self.actions}

    def validate(self, env: str) -> list[str]:
        warnings = []
        valid_actions = ["insert", "update", "upsert", "delete", "hash", "extract"]
        for action in self.actions:
            if action["action"] not in valid_actions:
                warnings.append(f"⚠️ {self.name}: Неизвестное действие '{action['action']}'")
        return warnings