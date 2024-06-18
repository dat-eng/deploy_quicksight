FROM       python:3.10-alpine as qsight

RUN        apk update
RUN        apk add openssl-dev libffi-dev openrc build-base gcc g++ cargo rust \
             coreutils bash make less

RUN        mkdir -p /app
WORKDIR    /app
COPY       . /app

RUN        pip install -r /app/requirements.txt

RUN        chmod 755 /app/bin/*.py /app/docker-entrypoint.sh

ENV        PYTHONPATH /app

# Docker entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD        ["pass"]