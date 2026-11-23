# syntax=docker/dockerfile:1

FROM docker.io/library/node:24.22.3-bookworm-slim@sha256:dc26ae92c9fb15cf6b1d63e20f0944b2efe0f115b20e00be48fb23fceb061c54 AS assets
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY grc/sass/ grc/sass/
RUN mkdir -p grc/static && npm run build

FROM python:3.12-bookworm@sha256:4f1cc04d959e1360fb4e6957e23e5cd96d32a239d996af6d5c7ad29ee55175d0 AS pillow
COPY docker/pillow-build-requirements.txt /build/
RUN apt-get update \
    && apt-get install -y --no-install-recommends cmake nasm rsync unzip libxau-dev \
    && apt-get install -y --only-upgrade libbrotli1 libbrotli-dev \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libbrotli1)" ge '1.0.9-2+deb12u1' \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libbrotli-dev)" ge '1.0.9-2+deb12u1' \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --only-binary=:all: -r /build/pillow-build-requirements.txt
COPY docker/build-pillow.sh docker/pillow-brotli.patch /build/
RUN bash /build/build-pillow.sh

FROM python:3.12-bookworm@sha256:4f1cc04d959e1360fb4e6957e23e5cd96d32a239d996af6d5c7ad29ee55175d0

ENV DOCKERIZE_VERSION v0.6.1
RUN wget -q https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apt update && apt-get install -y wkhtmltopdf

# Add network connectivity debugging tools
RUN apt-get update && apt-get install -y telnet iputils-ping net-tools curl

# Debian backports the Brotli security fix without changing the upstream version.
RUN apt-get update \
    && apt-get install -y --only-upgrade libbrotli1 libbrotli-dev \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libbrotli1)" ge '1.0.9-2+deb12u1' \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libbrotli-dev)" ge '1.0.9-2+deb12u1' \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 3000

RUN mkdir -p /app/
WORKDIR /app

COPY requirements.txt requirements.txt
COPY --from=pillow /wheelhouse/ /opt/pillow/
COPY docker/verify-pillow.py /tmp/verify-pillow.py
RUN pip install --no-cache-dir --no-deps /opt/pillow/*.whl \
    && pip install --no-cache-dir -r requirements.txt \
    && python /tmp/verify-pillow.py \
    && mkdir -p /usr/local/share/cgr \
    && cp /opt/pillow/*.txt /opt/pillow/*.json /opt/pillow/SHA256SUMS /usr/local/share/cgr/ \
    && rm -rf /opt/pillow /tmp/verify-pillow.py

COPY . .
COPY --from=assets /app/grc/static/app.css /app/grc/static/app.css.map /app/grc/static/

# Compile messages
RUN pybabel compile -d grc/translations

# Don't run as root user
USER 1000
CMD /app/run.sh
