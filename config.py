from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"] 

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING"]

    DB_HOST: str
    DB_PORT: int 
    DB_NAME: str 
    DB_USER: str 
    DB_PASS: str 
    
    TEST_DB_HOST: str 
    TEST_DB_PORT: int 
    TEST_DB_NAME: str 
    TEST_DB_USER: str 
    TEST_DB_PASS: str

    
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str


    REDIS_HOST: str 
    REDIS_PORT: int 
    REDIS_PASS: str 
    REDIS_APP_DB: int 
    REDIS_CELERY_DB: int
    REDIS_TEST_DB: int


    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_VHOST: str

    SECRET: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    AWS_ACCES_KEY_ID: str
    AWS_SECRET_ACCES_KEY: str
    REGION_NAME: str

    BUCKET_NAME: str
    TEST_BUCKET_NAME: str

    def build_test_postgres_dsn(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.TEST_DB_USER}:{self.TEST_DB_PASS}"
            f"@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    def build_postgres_dsn(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def build_app_redis_dsn(self) -> str:
        return (
            "redis://"
            f":{self.REDIS_PASS}@{self.REDIS_HOST}"
            f":{self.REDIS_PORT}/{self.REDIS_APP_DB}"
        )
    
    def build_celery_redis_dsn(self) -> str:
        return (
            "redis://"
            f":{self.REDIS_PASS}@{self.REDIS_HOST}"
            f":{self.REDIS_PORT}/{self.REDIS_CELERY_DB}"
        )
    
    def build_test_redis_dsn(self) -> str:
        return (
            "redis://"
            f":{self.REDIS_PASS}@{self.REDIS_HOST}"
            f":{self.REDIS_PORT}/{self.REDIS_TEST_DB}"
        )

    def build_rabbitmq_dsn(self) -> str:
        return (
            "amqp://"
            f"{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@"
            f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"
        )
    
    
    class Config:
        env_file = '.env'


settings = Settings()