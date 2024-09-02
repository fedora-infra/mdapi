FROM registry.fedoraproject.org/fedora:40

LABEL maintainer "Akashdeep Dhar <t0xic0der@fedoraproject.org>"

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

RUN dnf -y install python3-pip && dnf -y clean all
RUN pip install --upgrade mdapi==3.1.6a2

# Uncomment the following MDAPI_CONFIG and comment the other MDAPI_CONFIG for local development builds
# ENV MDAPI_CONFIG=/code/mdapi/confdata/standard.py

# For deployment purposes, make a custom configuration in the /etc/mdapi/confdata directory
ENV MDAPI_CONFIG=/etc/mdapi/confdata/myconfig.py

ENTRYPOINT mdapi -c $MDAPI_CONFIG serveapp
