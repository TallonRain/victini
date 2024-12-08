FROM python:3.12-alpine
LABEL org.opencontainers.image.source=https://github.com/TallonRain/victini
WORKDIR /data
COPY requirements.txt /data/requirements.txt
RUN ["pip", "install", "-r", "requirements.txt"]
ADD . /data
ENTRYPOINT ["python3", "main.py"]
