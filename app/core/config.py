import os

class Settings:
    PROJECT_NAME: str = "Multi-Vendor E-Commerce Platform"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-e-commerce-key-2026-multi-vendor-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for easy testing
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

settings = Settings()
