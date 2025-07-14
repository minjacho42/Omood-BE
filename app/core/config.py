from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    ALGORITHM: str
    REDIRECT_URI: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    SQLALCHEMY_DATABASE_URL: str
    LOG_DIR: str
    MONGODB_URI: str
    MONGO_DATABASE: str
    DEBUG: bool = False
    CLOUDFLARE_S3_URI: str
    CLOUDFLARE_ACCESS_KEY_ID: str
    CLOUDFLARE_SECRET_ACCESS_KEY: str
    CLOUDFLARE_BUCKET_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()