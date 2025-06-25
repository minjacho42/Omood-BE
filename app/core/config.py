from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
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

    class Config:
        env_file = ".env"

settings = Settings()