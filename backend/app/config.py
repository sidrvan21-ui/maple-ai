from pydantic_settings import BaseSettings, SettingsConfigDict

from app.rag.admit import repo_root


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(repo_root() / ".env"),
        extra="ignore",
    )

    jwt_secret: str = "dev-only-change-me"
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://127.0.0.1:8000/auth/google/callback"
    sso_allowed_domain: str = ""
    sso_default_role: str = "product"
    sso_role_map: str = ""
    allow_dev_login: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
