from .base import RetryConfig, TLSConfig, Exporter

class OTLPExporter(Exporter):
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.type = "otlp"
        self.endpoint = endpoint
        self.compression = "gzip"
        self.tls = TLSConfig()
        self.retry = RetryConfig()
        self.queue_enabled = True
        self.queue_size = 800

    def to_config(self) -> dict:
        config = {
            "endpoint": self.endpoint,
            "compression": self.compression,
            "retry_on_failure": self.retry.to_dict(),
            "sending_queue": {
                "enabled": self.queue_enabled,
                "queue_size": self.queue_size
            }
        }

        if self.tls.enabled:
            config["tls"] = self.tls.to_dict()

        return config

    def validate(self, env: str) -> list[str]:
        warnings = []
        if env == "prod" and (not self.tls.enabled or self.tls.insecure):
            warnings.append(f"⚠️ {self.name}: TLS отключен или небезопасен в production")
        return warnings


class PrometheusRemoteWriteExporter(Exporter):
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.type = "prometheusremotewrite"
        self.endpoint = endpoint
        self.timeout = "30s"
        self.send_metadata = True
        self.add_metric_suffixes = False
        self.retry = RetryConfig()
        self.resource_to_telemetry_conversion = True

    def to_config(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "timeout": self.timeout,
            "send_metadata": self.send_metadata,
            "add_metric_suffixes": self.add_metric_suffixes,
            "retry_on_failure": self.retry.to_dict(),
            "resource_to_telemetry_conversion": {
                "enabled": self.resource_to_telemetry_conversion
            }
        }

    def validate(self, env: str) -> list[str]:
        warnings = []
        if not self.endpoint.startswith("https://") and env == "prod":
            warnings.append(f"⚠️ {self.name}: Используется небезопасный HTTP в production")
        return warnings