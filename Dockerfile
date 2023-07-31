# Base image with python
FROM cgr.dev/chainguard/wolfi-base as base
ARG version=3.11
RUN apk add python-${version} py${version}-pip

# Intermediate layer
FROM base as builder

COPY . /root/code

RUN pip install build
RUN pip install -e /root/code

# Production

WORKDIR /app

CMD ["stats"]
