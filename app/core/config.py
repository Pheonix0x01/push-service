from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_url: str
    user_service_url: str
    template_service_url: str
    status_callback_url: str
    redis_url: str
    fcm_credentials_path: str
    jwt_secret: str
    max_retries: int = 5
    retry_backoff_base: int = 2
    server_host: str = "0.0.0.0"
    server_port: int = 8500
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()