FROM python:3.10-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE Purpose: Prevents Python from writing .pyc files (compiled bytecode) to disk.
# PYTHONUNBUFFERED        Purpose: Prevents Python from buffering stdout and stderr (it just writes them directly).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


WORKDIR /bookclub

RUN pip install poetry

COPY pyproject.toml .
RUN poetry install --no-root

COPY bookclub/bookclub /bookclub/

EXPOSE 8080

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]