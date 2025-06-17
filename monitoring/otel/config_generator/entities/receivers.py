from .base import Endpoint, TLSConfig, Receiver

from dataclasses import dataclass


class OTLPReceiver(Receiver):
    def __init__(
            self,
            name: str,
            http_endpoint: Endpoint,
            grpc_endpoint: Endpoint,
            grpc_tls: TLSConfig,
            http_tls: TLSConfig,
            http_include_metadata: bool = True
    ):
        self.type = "otlp"
        self.name = name
        self.grpc_endpoint = grpc_endpoint
        self.http_endpoint = http_endpoint
        self.grpc_compression = "gzip"
        self.grpc_tls = grpc_tls
        self.http_tls = http_tls
        self.http_include_metadata = http_include_metadata

    def to_config(self) -> dict:
        config = {
            "protocols": {
                "grpc": {
                    "endpoint": self.grpc_endpoint.to_string(),
                    "compression": self.grpc_compression
                },
                "http": {
                    "endpoint": self.http_endpoint.to_string(),
                    "include_metadata": self.http_include_metadata
                }
            }
        }

        if self.grpc_tls.enabled:
            config["protocols"]["grpc"]["tls"] = self.grpc_tls.to_dict()
        if self.http_tls.enabled:
            config["protocols"]["http"]["tls"] = self.http_tls.to_dict()

        return config

    def validate(self, env: str) -> list[str]:
        warnings = []

        if env == "prod":
            if not self.grpc_endpoint.is_secure():
                warnings.append(
                    f"⚠️ {self.name}: gRPC endpoint {self.grpc_endpoint.to_string()} небезопасен для production")
            if not self.http_endpoint.is_secure():
                warnings.append(
                    f"⚠️ {self.name}: HTTP endpoint {self.http_endpoint.to_string()} небезопасен для production")

            if not self.grpc_tls.enabled or self.grpc_tls.insecure:
                warnings.append(f"⚠️ {self.name}: gRPC TLS отключен или небезопасен в production")
            if not self.http_tls.enabled or self.http_tls.insecure:
                warnings.append(f"⚠️ {self.name}: HTTP TLS отключен или небезопасен в production")

        return warnings

@dataclass
class LabelConfig:
    source_labels: list[str]
    regexp: str
    target_label: str
    replacement: str

class PrometheusReceiver(Receiver):
    def __init__(
            self,
            name: str = "prometheus",
            scrape_interval: str = "15s",
            scrape_timeout: str = "10s",
            evaluation_interval: str = "15s",
    ):
        self.type = "prometheus"
        self.name = name
        self.scrape_interval = scrape_interval
        self.scrape_timeout = scrape_timeout
        self.evaluation_interval = evaluation_interval
        self.scrape_configs: list[dict] = []

    def add_scrape_config(
            self,
            job_name: str,
            targets: list[str],
            scrape_interval: str = None,
            relabel_configs: list[LabelConfig] = None,
    ) -> 'PrometheusReceiver':
        config = {
            "job_name": job_name,
            "static_configs": [{
                "targets": targets
            }],
        }
        if relabel_configs:
            config["relabel_configs"] = [
                {
                    "source_labels": relabel_config.source_labels,
                    "regexp": relabel_config.regexp,
                    "target_label": relabel_config.target_label,
                    "replacement": relabel_config.replacement,
                }
                for relabel_config in relabel_configs
            ]

        if scrape_interval:
            config["scrape_interval"] = scrape_interval

        self.scrape_configs.append(config)
        return self

    def to_config(self) -> dict:
        return {
            "config": {
                "global": {
                    "scrape_interval": self.scrape_interval,
                    "scrape_timeout": self.scrape_timeout,
                    "evaluation_interval": self.evaluation_interval
                },
                "scrape_configs": self.scrape_configs
            }
        }

    def validate(self, env: str) -> list[str]:
        warnings = []
        if not self.scrape_configs:
            warnings.append(f"⚠️ {self.name}: Нет настроенных scrape конфигураций")
        return warnings
