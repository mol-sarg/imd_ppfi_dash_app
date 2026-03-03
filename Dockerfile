FROM python:3.11-slim 

# needed for fiona/geopandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev \
    proj-bin proj-data libproj-dev \
    libgeos-dev \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt
ADD . /app/
# added preload to save ram on azure
CMD ["gunicorn", "--workers=1", "--threads=4", "--preload", "--timeout=600", "--bind", "0.0.0.0:8000", "app:server"]