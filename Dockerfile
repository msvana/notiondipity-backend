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

EXPOSE 5000
CMD ["poetry", "run", "python", "notiondipity_backend/main.py"]

