# Compatibility Dockerfile. Prefer infra/Dockerfile.core for new deployments.
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
COPY --chown=thalos:thalos pyproject.toml .
RUN chmod 0770 /app/STATELOG
USER thalos

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "services.control_plane.main:app", "--host", "0.0.0.0", "--port", "8000"]
