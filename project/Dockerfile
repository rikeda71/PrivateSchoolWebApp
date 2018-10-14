FROM python:3.6-alpine3.6
ENV PYTHONUNBUFFERED 1
RUN apk --update-cache \
    add musl \
    linux-headers \
    openjdk8 \
    poppler-utils \
    tesseract-ocr \
    gcc \
    g++ \
    make \
    gfortran \
    openblas-dev \
    build-base \
    jpeg-dev \
    zlib-dev \
    libffi-dev \
    mariadb-dev \
    wget
RUN wget -q -P /usr/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata \
    && wget -q -P /usr/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/master/jpn.traineddata
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
