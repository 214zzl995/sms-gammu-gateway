FROM python:3-alpine AS base

RUN echo 'http://ftp.halifax.rwth-aachen.de/alpine/latest-stable/community' >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache pkgconfig gammu gammu-libs gammu-dev

RUN python -m pip install -U pip

# Build dependencies in a dedicated stage
FROM base AS dependencies
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps libffi-dev openssl-dev gcc musl-dev python3-dev cargo \
    && pip install -r requirements.txt

# Switch back to base layer for final stage
FROM base AS final
ENV BASE_PATH /sms-gw
RUN mkdir $BASE_PATH /ssl
WORKDIR $BASE_PATH
COPY . $BASE_PATH

COPY --from=dependencies /root/.cache /root/.cache
RUN pip install -r requirements.txt && rm -rf /root/.cache

CMD [ "python", "./run.py" ]
