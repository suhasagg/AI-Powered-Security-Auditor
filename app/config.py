from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    llm_mode: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    zap_mode: str = "mock"
    authorized_hosts: str = "app.internal.example,localhost"
    policy_version: str = "2026-01"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def host_allowlist(self): return {x.strip().lower() for x in self.authorized_hosts.split(",") if x.strip()}
settings = Settings()
