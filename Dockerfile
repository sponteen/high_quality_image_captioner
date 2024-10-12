FROM python:3.12.6 AS image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV WORKSPACE /data

RUN apt-get update && \
    apt-get install -y nano sudo && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry

RUN poetry install --without dev

COPY . .

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH "${PYTHONPATH}:/app/"

COPY ./deploy/entrypoint.sh /

WORKDIR ${WORKSPACE}
ENTRYPOINT ["/entrypoint.sh"]

WORKDIR /app

CMD ["poetry", "run", "uvicorn", "src.src:app", "--host", "0.0.0.0", "--port", "8000"]
