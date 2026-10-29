# Thalos Prime Sentinel discovery service
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin thalos \
    && mkdir -p /app/STATELOG \
    && chown -R thalos:thalos /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=thalos:thalos core/ ./core/
COPY --chown=thalos:thalos services/ ./services/
COPY --chown=thalos:thalos STATELOG/ ./STATELOG/
RUN chmod 0770 /app/STATELOG

USER thalos
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "services.discovery_sentinel.mcp_server:app", "--host", "0.0.0.0", "--port", "8001"]
