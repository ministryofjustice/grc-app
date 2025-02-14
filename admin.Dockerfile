
# syntax=docker/dockerfile:1

FROM python:3.8

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN curl -SLO https://deb.nodesource.com/nsolid_setup_deb.sh
RUN chmod 500 nsolid_setup_deb.sh
RUN ./nsolid_setup_deb.sh 21
RUN apt-get install nodejs -y

RUN apt-get install -y wkhtmltopdf
ENV XDG_CACHE_HOME /tmp/cache
RUN mkdir -p /tmp/cache && chmod 777 /tmp/cache

EXPOSE 3001

RUN mkdir -p /app/
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# RUN pip install pre-commit
# RUN pre-commit install --install-hooks

RUN npm install
RUN npm run build

#RUN rm /app/grc -r
RUN chmod 777 /app/run_admin.sh

# Don't run as root user
USER 1000
CMD /app/run_admin.sh
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" "--port=5001"]