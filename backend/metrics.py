from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


# 配置资源信息
resource = Resource(attributes={
    "service.name": "python-demo-service",
    "service.version": "1.0.0",
    "service.namespace": "billing",          # 可选：逻辑域
    "deployment.environment": "production",  # 环境
    "service.instance.id": "host-42",        # 实例/容器唯一标识
})

# 设置 Tracer Provider
trace.set_tracer_provider(TracerProvider(resource=resource))

# 配置 OTLP Exporter (使用 HTTP)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",  # Jaeger 的 OTLP HTTP 端口
)

# 添加 Span Processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# 获取 tracer
tracer = trace.get_tracer(__name__)
