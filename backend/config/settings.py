import os
from dotenv import load_dotenv
from backend.constant import app_env as app_env_const
from backend.constant import jwt as jwt_const

load_dotenv()


class Settings:
    """Centralized configuration management for the application."""

    # Application Environment
    app_env: str = os.getenv("APP_ENV", app_env_const.UT)

    # Database Configuration
    db_user: str = os.getenv("MYSQL_USER")
    db_password: str = os.getenv("MYSQL_PASSWORD")
    db_host: str = os.getenv("MYSQL_HOST")
    db_port: str = os.getenv("MYSQL_PORT")
    db_name: str = os.getenv("MYSQL_DB_NAME")

    # JWT Configuration
    jwt_secret: str = os.getenv("JWT_SECRET", jwt_const.DEFAULT_SECRET)
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_hours: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # MinIO Configuration
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY")
    

    # Astronomy Net Configuration
    astronomy_net_endpoint: str = os.getenv(
        "ASTRONOMY_NET_ENDPOINT", "http://127.0.0.1:8001")

    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", None)
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    # SMTP Configuration
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER")
    smtp_password: str = os.getenv("SMTP_PASSWORD")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL")

    # Weather API Configuration
    weather_api_endpoint: str = os.getenv(
        "WEATHER_API_ENDPOINT", "https://api.open-meteo.com/v1/forecast")

    @property
    def redis_url(self) -> str:
        """Generate Redis connection URL from config parameters."""
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def sqlalchemy_database_url(self) -> str:
        """Generate SQLAlchemy database URL from config parameters."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def __init__(self):
        """Validate that all required settings are loaded."""
        # Validate app_env
        if self.app_env not in app_env_const.ALL:
            raise ValueError(
                f"Invalid APP_ENV value '{self.app_env}'. "
                f"Must be one of: {', '.join(sorted(app_env_const.ALL))}"
            )

        if self.app_env in [app_env_const.DEV, app_env_const.PROD]:
            required_fields = [
                "db_user",
                "db_password",
                "db_host",
                "db_port",
                "db_name",
            ]
            for field in required_fields:
                if getattr(self, field) is None:
                    raise ValueError(
                        f"Missing required environment variable: {field.upper()}"
                    )

        if self.app_env == app_env_const.PROD:
            if self.jwt_secret == jwt_const.DEFAULT_SECRET:
                raise ValueError(
                    f"defualt jwt secret can not be used in prod environment"
                )