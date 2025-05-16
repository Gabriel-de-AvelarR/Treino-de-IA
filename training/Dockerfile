FROM python:3.11-slim

WORKDIR /app

COPY ../models ./models
COPY ..data/ ./data

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "train.py"]