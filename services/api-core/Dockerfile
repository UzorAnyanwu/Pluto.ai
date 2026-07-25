# Build from the monorepo root, not this directory, because this service depends on the local
# libs/pluto_core package:
#   docker build -f services/api-core/Dockerfile -t pluto-api-core .
#
# Multi-stage: the builder stage has the full toolchain needed to compile any C-extension
# dependencies (asyncpg, argon2-cffi); the final image only carries the installed packages and
# application code, keeping the shipped image small and free of build tooling (smaller attack
# surface, faster cold starts on ECS Fargate).

FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY libs/pluto_core/ libs/pluto_core/
COPY services/api-core/ services/api-core/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install ./libs/pluto_core ./services/api-core

FROM python:3.12-slim AS runtime

RUN groupadd --system pluto && useradd --system --gid pluto --no-create-home pluto

COPY --from=builder /install /usr/local
COPY --from=builder /build/services/api-core/app /app/app

WORKDIR /app
USER pluto

EXPOSE 8000

# Liveness: does the process respond at all. Readiness (DB/Redis reachable) is a separate
# `/healthz/ready` endpoint added alongside the first non-auth module — not needed yet since
# ECS task placement for this milestone doesn't depend on it.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
