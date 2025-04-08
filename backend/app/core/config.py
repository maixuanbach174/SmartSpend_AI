from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: PostgresDsn | None = None
    
    class Config:
        env_file = "../.env"
        case_sensitive = True
    
    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()