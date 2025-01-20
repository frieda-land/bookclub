FROM python:3.10-slim

WORKDIR /bookclub

RUN pip install poetry

COPY pyproject.toml .
RUN poetry install --no-root

COPY bookclub/bookclub /bookclub/

EXPOSE 8080

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]