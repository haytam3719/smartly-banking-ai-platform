import contextvars, logging, sys
from pythonjsonlogger.json import JsonFormatter
request_id_var = contextvars.ContextVar("request_id", default="-")
correlation_id_var = contextvars.ContextVar("correlation_id", default="-")
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get(); record.correlation_id = correlation_id_var.get(); return True
def configure_logging():
    handler = logging.StreamHandler(sys.stdout); handler.addFilter(ContextFilter()); handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(correlation_id)s"))
    root = logging.getLogger(); root.handlers = [handler]; root.setLevel(logging.INFO)
