    FROM python:3.11-slim

    WORKDIR /.

    COPY chatbot .
    COPY models ./models


    RUN pip install --no-cache-dir -r requirements.txt

    EXPOSE 5000

    CMD ["python", "app.py"]

