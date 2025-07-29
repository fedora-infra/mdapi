LABEL maintainer "Akashdeep Dhar <t0xic0der@fedoraproject.org>"

# Builder image

FROM registry.fedoraproject.org/fedora-minimal:42 AS builder

RUN dnf update --assumeyes && dnf install wget createrepo_c-devel gcc tar gzip golang git --assumeyes --setopt=install_weak_deps=False && dnf clean all

WORKDIR /metasource

COPY . .

ENV CGO_ENABLED=1 GOOS=linux

RUN go mod download && go build -o meta

# Runtime image

FROM registry.fedoraproject.org/fedora-minimal:42 as runtime

RUN dnf update --assumeyes && dnf install createrepo_c-devel --assumeyes --setopt=install_weak_deps=False && dnf clean all && mkdir --parents /db

VOLUME ["/db"]

COPY --from=builder /metasource/meta /metasource/meta

EXPOSE 8080

ENTRYPOINT ["/metasource/meta"]
