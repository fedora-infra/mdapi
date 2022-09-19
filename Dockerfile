LABEL maintainer "Akashdeep Dhar <t0xic0der@fedoraproject.org>"

FROM fedora:36

EXPOSE 8080

COPY . /code
WORKDIR /code

ENV PYTHONUNBUFFERED=1
ENV MDAPI_CONFIG=/code/mdapi/confdata/myconfig.py

RUN dnf -y install python3-pip poetry && dnf -y clean all
RUN poetry config virtualenvs.create false && poetry install

ENTRYPOINT mdapi -c $MDAPI_CONFIG serveapp
