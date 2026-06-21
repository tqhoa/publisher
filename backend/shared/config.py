from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "publisher"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "info"
    port: int = 8000

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7

    # Cookie encryption — 32-byte base64-encoded key
    cookie_encryption_key: str

    # CORS
    allowed_origins: str = "http://localhost:5173"

    # Seed admin (first run)
    seed_admin_email: str = "admin@publisher.info"
    seed_admin_password: str = "Admin123!"

    # Celery
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # Browser Farm
    browser_max_sessions: int = 100
    browser_headless: bool = True
    browser_timeout_ms: int = 60000

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    model_config = {"env_file": ".env", "case_sensitive": False}  # type: ignore[misc]


settings = Settings()
