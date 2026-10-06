FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    make \
    gcc-12 \
    g++-12 \
    && rm -rf /var/lib/apt/lists/*

ENV CC=gcc-12
ENV CXX=g++-12

WORKDIR /app

# Install ethics_engine's own minimal deps first, mirroring its own Dockerfile
RUN pip install --no-cache-dir setuptools requests pyeda PyYAML

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cd ethics_engine && python setup.py install

EXPOSE 7860

CMD ["python", "app.py"]