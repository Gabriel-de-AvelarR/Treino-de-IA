FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
python3-venv \
build-essential \
&& rm -rf /var/lib/apt/lists/*

#Symlinks
RUN rm -f /usr/bin/python /usr/bin/pip && \
ln -s /usr/bin/python3 /usr/bin/python && \
ln -s /usr/bin/pip3 /usr/bin/pip

WORKDIR /.

COPY training .
COPY data ./data

RUN pip install --no-cache-dir --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

CMD ["python3", "train.py"]
