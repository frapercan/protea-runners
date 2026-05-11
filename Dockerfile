# Slim runtime image for the protea-runners experiment plugins.
#
# Bundles the lightgbm, knn, and baseline experiment runners as a
# library image. Discovery is via the protea.runners entry-point group.

FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.2

COPY pyproject.toml README.md ./
COPY poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

COPY src/ ./src/
RUN poetry install --only main --no-interaction --no-ansi

FROM python:3.12-slim

# libgomp1 is needed at runtime by numpy / lightgbm.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Library image: importable as protea_runners with the lightgbm / knn /
# baseline plugin entry-points registered.
CMD ["python", "-c", "import protea_runners; print('protea-runners', protea_runners.__name__, 'ready')"]
