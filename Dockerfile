FROM registry.fedoraproject.org/fedora:36

LABEL maintainer "Akashdeep Dhar <t0xic0der@fedoraproject.org>"

EXPOSE 8080

COPY . /code
WORKDIR /code

ENV PYTHONUNBUFFERED=1

RUN rm -rf /code/poetry.lock
RUN dnf -y install python3-pip poetry && dnf -y clean all
RUN poetry config virtualenvs.create false && poetry install

# Uncomment the following MDAPI_CONFIG and comment the other MDAPI_CONFIG for local development builds
# ENV MDAPI_CONFIG=/code/mdapi/confdata/standard.py

# For deployment purposes, make a custom configuration in the /etc/mdapi/confdata directory
ENV MDAPI_CONFIG=/etc/mdapi/confdata/myconfig.py

ENTRYPOINT mdapi -c $MDAPI_CONFIG serveapp
