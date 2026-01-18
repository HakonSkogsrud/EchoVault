FROM python:3.13-slim

WORKDIR /app

RUN pip install uv && \
    groupadd -r appuser && \
    useradd -r -g appuser -m appuser && \
    chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser uv.lock pyproject.toml ./
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser README.md ./

RUN uv sync && \
    uv pip install --no-cache .

EXPOSE 8000

CMD ["uv", "run", "chainlit", "run", "src/frontend.py", "--host", "0.0.0.0", "--port", "8000"]
