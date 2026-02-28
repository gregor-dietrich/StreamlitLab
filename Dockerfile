FROM python:3.14.3-alpine3.23

ENV LANGUAGE='en_US:en'

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && rm requirements.txt

COPY .streamlit .streamlit
COPY main.py .
COPY src/ src/

EXPOSE 80

ENTRYPOINT [ "streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=80" ]
CMD []
