"""OpenTelemetry instrumentation for observability."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from ..config import telemetry


def setup_telemetry():
    """Initialize OpenTelemetry tracing."""
    resource = Resource(attributes={
        SERVICE_NAME: telemetry.service_name,
    })
    
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=telemetry.endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    
    trace.set_tracer_provider(provider)


def get_tracer(name: str = "vectordb-learn") -> trace.Tracer:
    """Get a tracer instance."""
    return trace.get_tracer(name)
