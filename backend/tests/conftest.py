import base64
import os

# Set env vars before any app imports
_test_key = base64.b64encode(os.urandom(32)).decode()
os.environ.setdefault("COOKIE_ENCRYPTION_KEY", _test_key)
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://publisher:publisher@localhost/publisher_test")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-at-least-32-characters-long!!")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/14")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/13")
