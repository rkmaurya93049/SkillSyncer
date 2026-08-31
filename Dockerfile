FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libgomp is required by common numerical/ML wheels used by sentence-transformers.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Docker Spaces run as uid 1000. Keep the application and cache writable.
RUN useradd -m -u 1000 user \
    && mkdir -p /data \
    && chown -R user:user /data

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface \
    SKILLSYNCER_DB_PATH=/data/evaluations.db

WORKDIR /home/user/app

COPY --chown=user backend/requirements-hf.txt ./backend/requirements-hf.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r backend/requirements-hf.txt

COPY --chown=user backend ./backend

# Cache the semantic-similarity model during the image build so the first API
# request does not need to download model weights.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

EXPOSE 7860

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
