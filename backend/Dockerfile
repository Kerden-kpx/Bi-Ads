FROM python:3.11-slim-bookworm

# 可选：切换APT镜像（默认不改源），可在构建时传 APT_MIRROR=mirrors.aliyun.com
ARG APT_MIRROR=

# Prevent python from writing pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH="/home/app/.local/bin:$PATH"

# 可选：pip 镜像（国内可在构建时覆盖），默认官方
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_EXTRA_INDEX_URL=https://pypi.org/simple
# Allow overriding trusted hosts (useful behind HTTPS-intercepting proxies or when switching mirrors)
ARG PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org"
ENV PIP_INDEX_URL=${PIP_INDEX_URL} \
    PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL} \
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}

WORKDIR /app

# System deps (curl for healthcheck)
RUN set -e; \
    if [ -n "${APT_MIRROR}" ]; then \
        case "${APT_MIRROR}" in \
            *://*) APT_MIRROR_URL="${APT_MIRROR}" ;; \
            *) APT_MIRROR_URL="https://${APT_MIRROR}" ;; \
        esac; \
        if [ -f /etc/apt/sources.list ]; then \
            sed -i "s@https\?://[^ ]\+debian.org@${APT_MIRROR_URL}@g" /etc/apt/sources.list; \
        fi; \
        if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
            sed -i "s@https\?://[^ ]\+debian.org@${APT_MIRROR_URL}@g" /etc/apt/sources.list.d/debian.sources; \
        fi; \
    fi; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=5 update; \
    apt-get install -y --no-install-recommends curl ca-certificates; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# More tolerant install: longer timeout, more retries, and optional trusted hosts for flaky networks
# Use BuildKit cache mounts for pip to speed up repeated builds.
# Requires building with DOCKER_BUILDKIT=1 and COMPOSE_DOCKER_CLI_BUILD=1
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pip-wheel \
    pip install --prefer-binary --default-timeout=600 --retries 10 -r requirements.txt

# Copy application code
COPY . .

EXPOSE 7800

# Allow overriding workers via env; default 4
ENV WORKERS=4

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://127.0.0.1:7800/health || exit 1

# Use gunicorn with uvicorn workers for prod
# 增加可配置超时时间（默认 600s）以避免长时间同步任务被 gunicorn 杀掉
CMD ["sh", "-c", "gunicorn main:app \
  --workers ${WORKERS:-4} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:7800 \
  --timeout ${TIMEOUT:-600} \
  --graceful-timeout ${GRACEFUL_TIMEOUT:-120} \
  --keep-alive ${KEEP_ALIVE:-75} \
  --access-logfile - \
  --error-logfile -"]
