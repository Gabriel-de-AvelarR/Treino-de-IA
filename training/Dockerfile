FROM python:3.11-slim

WORKDIR /.

COPY training .
COPY data ./data
COPY models ./models

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "train.py"]