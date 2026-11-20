# syntax=docker/dockerfile:1

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

FROM python:3.12@sha256:7d2d1e77c502be39a89f89d02a9abf105b41569ab595e450f42ac32b95b5f052

ENV DOCKERIZE_VERSION v0.6.1
RUN wget -q https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# This pinned Python base is Trixie, whose Brotli fix has a different revision.
RUN apt-get update \
    && apt-get install -y --only-upgrade libbrotli1 libbrotli-dev \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libbrotli1)" ge '1.1.0-2+deb13u1' \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libbrotli-dev)" ge '1.1.0-2+deb13u1' \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 3003

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

RUN chmod 777 /app/run_jwks.sh

# Don't run as root user
USER 1000
CMD /app/run_jwks.sh
