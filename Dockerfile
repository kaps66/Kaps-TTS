FROM nvidia/cuda:12.6.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[gpu]"

COPY kaps/ ./kaps/
COPY demo/ ./demo/

EXPOSE 8000
CMD ["python", "-m", "kaps.server"]
