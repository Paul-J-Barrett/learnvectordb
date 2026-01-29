"""Structured logging configuration with OpenTelemetry OTLP export."""

import logging
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.semconv.resource import ResourceAttributes
import structlog


def setup_logging():
    """Configure structured logging with OpenTelemetry OTLP export at DEBUG level."""
    resource = Resource(attributes={
        SERVICE_NAME: "vectordb-learn",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
    })

    if _logs.get_logger_provider() is None:
        provider = LoggerProvider(resource=resource)
        exporter = OTLPLogExporter(endpoint="http://dockerhost:4318/v1/logs")
        provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        _logs.set_logger_provider(provider)

    handler = LoggingHandler()
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    )
