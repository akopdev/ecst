# Base image with python
FROM cgr.dev/chainguard/wolfi-base as base
ARG version=3.11
RUN apk add python-${version} py${version}-pip

# Intermediate layer
FROM base as builder

COPY . ./

RUN pip install wheel
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /root/wheels -e .
RUN python setup.py bdist_wheel --dist-dir /root/wheels

# Production
FROM base as final

COPY --from=builder /root/wheels /wheels

RUN pip install --no-cache /wheels/*

CMD ["stats"]
