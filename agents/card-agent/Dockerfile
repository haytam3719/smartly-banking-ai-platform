FROM python:3.12.7-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN addgroup --system card && adduser --system --ingroup card --uid 10001 card
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
USER card
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"
CMD ["uvicorn", "card_agent.main:app", "--host", "0.0.0.0", "--port", "8080"]

