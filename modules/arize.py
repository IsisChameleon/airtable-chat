import os

# Import open-telemetry dependencies
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Import the automatic instrumentor from OpenInference
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
ARIZE_SPACE_KEY = os.environ['ARIZE_SPACE_KEY']
ARIZE_API_KEY = os.environ['ARIZE_API_KEY']

def setupInstrumentation():
    # Set the Space and API keys as headers for authentication
    headers = f"space_key={ARIZE_SPACE_KEY},api_key={ARIZE_API_KEY}"
    os.environ['OTEL_EXPORTER_OTLP_TRACES_HEADERS'] = headers

    # Set resource attributes for the name and version for your application
    model_id = 'airtable-chatbot' # Set this to any name you'd like for your app
    model_version = '0.1' # Use this to track metrics for different versions i.e. "1.0"
    resource = Resource(
        attributes={
            "model_id":model_id,
            "model_version":model_version,
        }
    )

    # Define the span processor as an exporter to the desired endpoint
    endpoint = "https://otlp.arize.com/v1"
    span_exporter = OTLPSpanExporter(endpoint=endpoint)
    span_processor = SimpleSpanProcessor(span_exporter=span_exporter)

    # Set the tracer provider
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    tracer_provider.add_span_processor(span_processor=span_processor)
    trace_api.set_tracer_provider(tracer_provider=tracer_provider)

    # Finish automatic instrumentation
    LlamaIndexInstrumentor().instrument()