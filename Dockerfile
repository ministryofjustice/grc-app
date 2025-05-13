
# syntax=docker/dockerfile:1

FROM python:3.10

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Install Node
RUN curl -SLO https://deb.nodesource.com/nsolid_setup_deb.sh
RUN chmod 500 nsolid_setup_deb.sh
RUN ./nsolid_setup_deb.sh 21
RUN apt-get install nodejs -y

RUN apt-get install -y wkhtmltopdf

# Add network connectivity debugging tools
RUN apt-get update && apt-get install -y telnet iputils-ping net-tools curl

EXPOSE 3000

RUN mkdir -p /app/
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN npm install
RUN npm run build

# Compile messages
RUN pybabel compile -d grc/translations

# Don't run as root user
# USER 1000
CMD /app/run.sh