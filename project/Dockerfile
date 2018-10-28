FROM python:3.6-alpine3.6
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /
RUN apk add --update-cache --no-cache \
        --virtual=.build-dependencies gcc g++ gfortran make && \
    apk add openjdk8 \
            poppler-utils \
            tesseract-ocr \
            jpeg-dev \
            zlib-dev \
            libffi-dev \
            mariadb-dev \
            wget && \
    wget -q -P /usr/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata && \
    wget -q -P /usr/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/master/jpn.traineddata && \
    pip --no-cache-dir install -r requirements.txt && \
    rm -f requirements.txt && \
    apk del .build-dependencies && \
    find /usr/local/lib/python3.*/ -name 'tests' -exec rm -r '{}' + && \
    find /usr/local/lib/python3.*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; && \
    mkdir /code
WORKDIR /code
