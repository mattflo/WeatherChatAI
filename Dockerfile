FROM python:3.10-bullseye

RUN pip3 install poetry

COPY pyproject.toml poetry.lock /app/

WORKDIR /app

RUN set -eux; \
    poetry config virtualenvs.create false; \
    poetry install --no-dev --no-interaction --no-ansi --no-root

COPY . /app/

RUN poetry run python -m app init_db

ENV PYTHONUNBUFFERED=1

EXPOSE 8080/tcp

CMD ["poetry", "run", "chainlit", "run", "fly_app.py", "-h", "--port", "8080"]
