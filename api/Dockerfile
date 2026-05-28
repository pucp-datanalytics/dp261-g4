FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=handoff/model/c_final_model.pkl \
    PREPROCESSOR_PATH=handoff/model/c_preprocessing_pipeline.pkl \
    THRESHOLD=0.5 \
    MODEL_VERSION=c_final_model

WORKDIR /app

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

COPY api/ /app/api/
COPY src/ /app/src/
COPY handoff/ /app/handoff/
COPY models/c_best_model_metadata.json /app/models/c_best_model_metadata.json

RUN useradd -m appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
