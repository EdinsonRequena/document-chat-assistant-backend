FROM python:3.11

WORKDIR /app

COPY Pipfile* ./
RUN pip install --no-cache-dir pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --system

COPY src ./src

ENV PYTHONPATH=/app/src

CMD ["bash","-lc","uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]