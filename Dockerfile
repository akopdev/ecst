ARG python=3.11

# Intermediate layer
FROM python:${python}-slim as builder

COPY requirements.txt /root/requirements.txt


RUN pip wheel -r /root/requirements.txt --wheel-dir=/root/wheels

# Production
FROM python:${python}-slim as production

# Get Build Hash From CI
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# We still have some production dependencies
RUN apt-get update && rm -rf /var/lib/apt/lists/*

# Get all pre-build stuff
COPY --from=builder /root/requirements.txt ./requirements.txt
COPY --from=builder /root/wheels /root/wheels

# So far poetry doesn't respect pip env vars likes PIP_WHEEL_DIR/PIP_FIND_LINKS
# that's why we should use pip itself.
RUN pip install --no-cache-dir --no-index --find-links=/root/wheels -r requirements.txt

COPY . ./

