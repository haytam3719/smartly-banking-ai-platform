FROM python:3.12.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN addgroup --system policy && adduser --system --ingroup policy --uid 10001 policy
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
USER policy
EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/health', timeout=2)"
CMD ["uvicorn", "policy_engine.main:app", "--host", "0.0.0.0", "--port", "8081"]

