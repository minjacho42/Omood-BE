# =========================
# Build stage (deps wheelize)
# =========================
FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# 시스템 기본 도구 (빌드용); 나중에 런타임 이미지엔 포함 안 됨
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 먼저 캐시
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# =========================
# Runtime stage
# =========================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 비루트 유저
RUN useradd -m -u 1000 appuser

WORKDIR /app

# 빌드 단계에서 만들어 둔 wheels만 설치 → 이미지 작게, 빠르게
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
 && rm -rf /wheels

# 앱 소스 복사
COPY . .

# 권한
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 실제 엔트리(필요 시 --workers, --log-level 등 추가)
# app.main:app 부분을 프로젝트 엔트리에 맞게 수정하세요.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
