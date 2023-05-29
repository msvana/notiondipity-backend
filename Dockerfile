FROM python:3.10-slim

ENV POETRY_VERSION=1.4.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"
WORKDIR /app

COPY poetry.lock pyproject.toml ./
COPY . /app
RUN poetry install

EXPOSE 5001
CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "--access-logfile=-",  "notiondipity_backend.main:app"]

