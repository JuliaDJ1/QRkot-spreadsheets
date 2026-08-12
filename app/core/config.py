from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    app_description: str = 'Сервис для поддержки котиков'
    database_url: str = 'sqlite+aiosqlite:///./qrkot.db'
    secret: str = 'SECRET'
    yandex_disk_token: Optional[str] = None
    report_format: str = '%Y%m%d_%H%M%S'

    class Config:
        env_file = '.env'


settings = Settings()
