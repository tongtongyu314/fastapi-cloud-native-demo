import os


class Settings:
    port: int = int(os.getenv("PORT", "8000"))
    app_env: str = os.getenv("APP_ENV", "dev")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")


settings = Settings()
