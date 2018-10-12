FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN apk --update-cache \
    add musl \
    linux-headers \
    gcc \
    g++ \
    make \
    gfortran \
    openblas-dev \
    build-base \
    jpeg-dev \
    zlib-dev \
    libffi-dev \
    mariadb-dev
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
