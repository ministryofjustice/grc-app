
# syntax=docker/dockerfile:1

FROM python:3.12@sha256:7d2d1e77c502be39a89f89d02a9abf105b41569ab595e450f42ac32b95b5f052

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

EXPOSE 3003

RUN mkdir -p /app/
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod 777 /app/run_jwks.sh

# Don't run as root user
USER 1000
CMD /app/run_jwks.sh