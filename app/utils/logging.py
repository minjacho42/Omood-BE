import os
import sys
from loguru import logger
from app.core.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

# 메인 애플리케이션 로그 (JSON)
logger.add(f"{settings.LOG_DIR}/app.json", serialize=True, rotation="10 MB", retention="7 days")

# 에러만 따로 저장 (선택)
logger.add(f"{settings.LOG_DIR}/error.json", serialize=True, level="ERROR", rotation="5 MB", retention="30 days")

# 콘솔 출력 (컬러)
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")