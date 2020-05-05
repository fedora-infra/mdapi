# This Dockerfile is used to build the mdapi service on Openshift
# mdapi.cfg configuration is managed by Openshift as a configmap
FROM fedora:31

LABEL maintainer "Clément Verna <cverna@fedoraproject.org>"

EXPOSE 8080

RUN dnf -y install python3-aiohttp python3-requests python3-fedora-messaging python3-uvloop python3-pip python3-gunicorn\
    && dnf clean all \
    && pip3 install aiosqlite

ENV MDAPI_CONFIG=/etc/mdapi/mdapi.cfg
COPY . /code
WORKDIR /code
ENTRYPOINT ["gunicorn", "mdapi.server:init_app", "--bind", "0.0.0.0:8080", "--worker-class", "aiohttp.GunicornUVLoopWebWorker", "-w", "2"]
