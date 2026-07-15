import os


class Config:
    """Central configuration for the Placement Portal application."""

    BASE_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
        )
    )

    # Flask
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "placement-portal-development-key",
    )

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///site.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = os.getenv(
        "SECURITY_PASSWORD_SALT",
        "placement-portal-development-salt",
    )
    SECURITY_TOKEN_AUTHENTICATION_HEADER = (
        "Authentication-Token"
    )

    # Admin account
    ADMIN_EMAIL = os.getenv(
        "ADMIN_EMAIL",
        "admin@placement.edu",
    )
    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@123",
    )

    # Redis cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv(
        "CACHE_REDIS_URL",
        "redis://127.0.0.1:6379/0",
    )
    CACHE_DEFAULT_TIMEOUT = 300

    # Redis
    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://127.0.0.1:6379/1",
    )

    # Exported CSV files
    EXPORT_FOLDER = os.path.join(
        BASE_DIR,
        "exports",
    )

    # Student resume files
    RESUME_FOLDER = os.path.join(
        BASE_DIR,
        "uploads",
        "resumes",
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Mail
    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "localhost",
    )
    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            "1025",
        )
    )
    MAIL_USE_TLS = (
        os.getenv(
            "MAIL_USE_TLS",
            "false",
        ).lower()
        == "true"
    )
    MAIL_USE_SSL = (
        os.getenv(
            "MAIL_USE_SSL",
            "false",
        ).lower()
        == "true"
    )
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = (
        "Placement Portal",
        os.getenv(
            "MAIL_DEFAULT_SENDER",
            "noreply@placement.local",
        ),
    )