import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
def configure_tracing():
    provider=TracerProvider(resource=Resource.create({"service.name":"card-agent"}));endpoint=os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    if endpoint:provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)

