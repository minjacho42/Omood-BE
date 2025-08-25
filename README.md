# Omood API

<p align="center"\>
<img src="src/omood.svg" alt="Omood Logo" width="150"/\>
</p\>

<p align="center"\>
<strong\>뽀모도로 세션과 멀티미디어 메모를 위한 백엔드 API</strong\>
</p\>


## 🧠 프로젝트 개요

**Omood**는 뽀모도로 타이머와 멀티미디어 메모 기능을 결합하여, 사용자의 집중 세션과 아이디어를 효과적으로 기록하고 관리하는 생산성 도구의 백엔드 API입니다.

단순한 시간 관리를 넘어, 각 세션 동안 떠오른 생각이나 자료를 텍스트, 이미지, 음성 등 다양한 형태로 즉시 기록하고 이를 날짜별로 조회하며 하루를 회고할 수 있는 경험을 제공합니다.

-----

## ✨ 주요 구현 사항

### 1\. Polyglot Persistence 아키텍처

데이터의 성격과 요구사항에 따라 최적의 데이터베이스를 조합하여 사용하는 **'다중 저장소'** 전략을 채택했습니다. 이를 통해 데이터 무결성, 유연성, 확장성을 모두 확보했습니다.

  * **PostgreSQL (RDBMS)**: 사용자 계정 정보와 같이 **정형화되어 있고 트랜잭션과 정합성이 중요한 데이터**를 저장합니다. SQLAlchemy를 통해 관리합니다.
  * **MongoDB (NoSQL)**: 태그, 첨부파일 등 **스키마가 유동적이고 비정형적인 데이터**(메모, 세션 기록)를 저장합니다. 빠른 읽기/쓰기 속도와 유연한 데이터 모델링의 이점을 활용합니다.

### 2\. Redis를 활용한 상태 관리 및 비동기 처리

실시간 데이터 처리와 시스템 부하 분산을 위해 Redis를 적극적으로 활용했습니다.

  * **현재 세션 상태 캐싱**: 사용자가 진행 중인 세션의 ID를 Redis에 `Key-Value` 형태로 저장하여, DB 조회 없이도 현재 상태를 O(1) 시간 복잡도로 빠르게 가져올 수 있도록 설계했습니다.
  * **백그라운드 워커 구현**: Redis의 `Sorted Set`을 타임라인 큐로 활용, 세션 만료 시간을 score로 저장합니다. 별도의 비동기 워커(`session_watcher`)가 주기적으로 만료 시간이 지난 세션을 조회하고 상태를 '완료'로 업데이트하여, **메인 애플리케이션의 부하 없이 예약 작업을 안정적으로 처리**합니다.

### 3\. 안전하고 효율적인 파일 처리

이미지, 음성 등 대용량 바이너리 파일을 안전하게 관리하기 위해 오브젝트 스토리지를 도입했습니다.

  * **Cloudflare R2 (S3 호환)**: 모든 첨부 파일을 본 서버가 아닌 외부 오브젝트 스토리지에 저장하여 서버의 부담을 줄이고, 향후 스토리지 확장에 유연하게 대처할 수 있도록 구성했습니다.
  * **Presigned URL**: 파일을 조회할 때, 스토리지에 직접 접근할 수 있는 임시 URL을 생성하여 클라이언트에 제공합니다. 이를 통해 **인증된 사용자만 제한된 시간 동안 안전하게 파일에 접근**할 수 있으며, 서버를 거치지 않고 클라이언트가 스토리지와 직접 통신하므로 트래픽을 효율적으로 관리할 수 있습니다.

### 4\. Docker 기반의 재현 가능한 개발/배포 환경

**Multi-stage Build** 전략을 사용하여 Dockerfile을 작성했습니다. 빌드에만 필요한 `build-essential` 같은 라이브러리들은 최종 이미지에서 제외하고, Python 의존성은 `wheel` 형태로 미리 빌드하여 설치 시간을 단축했습니다. 그 결과, **배포 이미지의 크기를 최적화**하고 보안을 강화하며, 어느 환경에서든 동일한 실행을 보장하는 기반을 마련했습니다.

-----

## 🔄 API Endpoints

| Method | Path                  | Description                      |
| :----- | :-------------------- | :------------------------------- |
| `POST` | `/auth/google/callback` | 구글 소셜 로그인 콜백            |
| `POST` | `/auth/logout`        | 로그아웃                         |
| `GET`  | `/user/me`            | 내 정보 조회                     |
| `POST` | `/memo`               | 메모 생성                        |
| `GET`  | `/memo/list`          | 기간별 메모 목록 조회            |
| `GET`  | `/memo/{memo_id}`     | 특정 메모 조회                   |
| `PUT`  | `/memo/{memo_id}`     | 메모 수정                        |
| `DELETE` | `/memo/{memo_id}`     | 메모 삭제                        |
| `POST` | `/session`            | 뽀모도로 세션 생성               |
| `GET`  | `/session/list`       | 기간별 세션 목록 조회            |
| `GET`  | `/session/current`    | 현재 진행 중인 세션 조회         |
| `GET`  | `/session/{session_id}` | 특정 세션 조회                   |
| `PUT`  | `/session/{session_id}` | 세션 정보 수정 (목표, 시간 등) |
| `PUT`  | `/session/{session_id}/status` | 세션 상태 변경 (시작, 중지 등) |
| `DELETE` | `/session/{session_id}` | 세션 삭제                        |

-----

## 🚀 실행 방법

#### 1\. 환경 변수 설정

프로젝트 루트 디렉터리에 `.env` 파일을 생성하고, 아래와 같이 필요한 환경 변수들을 직접 설정해야 합니다. (`app/core/config.py` 파일을 참고하세요.)

```env
# 예시
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
SECRET_KEY="your_jwt_secret_key"
ALGORITHM="HS256"
REDIRECT_URI="http://127.0.0.1:8000/auth/google/callback"
REDIS_HOST="redis"
REDIS_PORT=6379
SQLALCHEMY_DATABASE_URL="postgresql+asyncpg://user:password@host/db"
MONGODB_URI="mongodb://user:password@host"
# ... Cloudflare R2 관련 변수 등
```

#### 2\. Docker를 이용한 실행 (권장)

```sh
# Docker 이미지 빌드
docker build -t omood-api .

# Docker 컨테이너 실행 (생성한 .env 파일 사용)
docker run -d -p 8000:8000 --env-file .env omood-api
```

#### 3\. 로컬 환경에서 직접 실행

```sh
# 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# FastAPI 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
