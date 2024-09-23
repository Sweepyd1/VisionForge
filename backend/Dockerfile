FROM python:3.11

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && poetry install --no-root

COPY src ./src

CMD ["python", "src/app.py"]