# This Dockerfile is used to build the mdapi service on Openshift
# mdapi.cfg configuration is managed by Openshift as a configmap
FROM registry.fedoraproject.org/fedora:latest

LABEL maintainer "Clément Verna <cverna@fedoraproject.org>"

EXPOSE 8080

RUN dnf -y install python3-aiohttp python3-werkzeug python3-requests python3-sqlalchemy python3-fedora-messaging

USER 1001
ENV MDAPI_CONFIG=/etc/mdapi/mdapi.cfg
COPY . /code
ENTRYPOINT ["/code/mdapi-run"]
