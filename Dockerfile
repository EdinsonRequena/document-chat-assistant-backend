FROM python:3.11

WORKDIR /app

COPY Pipfile* ./
RUN pip install pipenv && pipenv install --deploy --system

COPY src ./src

ENV PYTHONPATH=/app/src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]