import yaml

from pkg.config_generator.otel.entities import *


class OTelCollectorConfigBuilder:
    def __init__(self, environment: str):
        self.environment = environment
        self.receivers: dict = {}
        self.processors: dict = {}
        self.exporters: dict = {}
        self.pipelines: dict = {}
        self.extensions: dict = {}


    def add_receiver(self, receiver: Receiver) -> 'OTelCollectorConfigBuilder':
        self.receivers[receiver.name] = receiver
        return self

    def add_processor(self, processor: Processor) -> 'OTelCollectorConfigBuilder':
        self.processors[processor.name] = processor
        return self

    def add_exporter(self, exporter: Exporter) -> 'OTelCollectorConfigBuilder':
        self.exporters[exporter.name] = exporter
        return self

    def add_pipeline(self, pipeline: Pipeline) -> 'OTelCollectorConfigBuilder':
        self.pipelines[f"{pipeline.telemetry_type.value}/{pipeline.name}"] = pipeline
        return self

    def add_extension(self, name: str, port: int) -> 'OTelCollectorConfigBuilder':
        self.extensions[name] = Extension(name, Endpoint(port=port))
        return self

    def validate(self) -> list[str]:
        warnings = []

        for receiver in self.receivers.values():
            warnings.extend(receiver.validate(self.environment))

        for processor in self.processors.values():
            warnings.extend(processor.validate(self.environment))

        for exporter in self.exporters.values():
            warnings.extend(exporter.validate(self.environment))

        for pipeline in self.pipelines.values():
            warnings.extend(pipeline.validate())

            for receiver_name in pipeline.receivers:
                if receiver_name not in self.receivers:
                    warnings.append(f"❌ Pipeline {pipeline.name}: receiver '{receiver_name}' не существует")

            for processor_name in pipeline.processors:
                if processor_name not in self.processors:
                    warnings.append(f"❌ Pipeline {pipeline.name}: processor '{processor_name}' не существует")

            for exporter_name in pipeline.exporters:
                if exporter_name not in self.exporters:
                    warnings.append(f"❌ Pipeline {pipeline.name}: exporter '{exporter_name}' не существует")

        if not self.pipelines:
            warnings.append("❌ Нет настроенных pipelines")

        return warnings

    def build(self) -> str:
        config = {}

        if self.receivers:
            config["receivers"] = {}
            for name, receiver in self.receivers.items():
                if receiver.enabled:
                    config["receivers"][name] = receiver.to_config()

        if self.processors:
            config["processors"] = {}
            for name, processor in self.processors.items():
                if processor.enabled:
                    config["processors"][name] = processor.to_config()

        if self.exporters:
            config["exporters"] = {}
            for name, exporter in self.exporters.items():
                if exporter.enabled:
                    config["exporters"][name] = exporter.to_config()

        if self.extensions:
            config["extensions"] = {}
            for name, extension in self.extensions.items():
                config["extensions"][name] = extension.to_config()

        service = {}

        if self.extensions:
            service["extensions"] = list(self.extensions.keys())

        if self.pipelines:
            service["pipelines"] = {}
            for key, pipeline in self.pipelines.items():
                if pipeline.enabled:
                    service["pipelines"][key] = pipeline.to_config()

        config["service"] = service

        return yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)


# === Пример использования ===

def example_usage():


    return config_yaml
