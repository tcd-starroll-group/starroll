import os
from dotenv import load_dotenv
from backend.constant import app_env as app_env_const
from backend.constant import jwt as jwt_const

load_dotenv()


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


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
    minio_secure: bool = _parse_bool(os.getenv("MINIO_SECURE"), default=False)

    # Astronomy Net Configuration
    astronomy_net_endpoint: str = os.getenv(
        "ASTRONOMY_NET_ENDPOINT", "http://127.0.0.1:8001")

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

            minio_required_fields = [
                "minio_endpoint",
                "minio_access_key",
                "minio_secret_key",
            ]
            for field in minio_required_fields:
                if getattr(self, field) in (None, ""):
                    raise ValueError(
                        f"Missing required environment variable: {field.upper()}"
                    )

        if self.app_env == app_env_const.PROD:
            if self.jwt_secret == jwt_const.DEFAULT_SECRET:
                raise ValueError(
                    f"defualt jwt secret can not be used in prod environment"
                )
