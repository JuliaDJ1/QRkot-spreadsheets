from http import HTTPStatus
from typing import AsyncGenerator

import httpx
from fastapi import HTTPException

from app.core.config import settings

YANDEX_DISK_API = 'https://cloud-api.yandex.net/v1/disk/resources'
FOLDER_NAME = 'QRKot Reports'


class YandexDiskClient:
    """Клиент для работы с API Яндекс Диска."""

    def __init__(self, token: str):
        self._token = token
        self._client: httpx.AsyncClient = None

    async def __aenter__(self) -> 'YandexDiskClient':
        self._client = httpx.AsyncClient(
            headers={'Authorization': f'OAuth {self._token}'}
        )
        await self._create_folder()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.aclose()

    async def _create_folder(self) -> None:
        """Создать папку QRKot Reports, если её нет."""
        response = await self._client.put(
            YANDEX_DISK_API,
            params={'path': FOLDER_NAME},
        )
        if response.status_code not in (
            HTTPStatus.CREATED, HTTPStatus.CONFLICT
        ):
            response.raise_for_status()

    async def create_excel_file(self, filename: str) -> str:
        """Получить ссылку для загрузки файла на Диск."""
        path = f'{FOLDER_NAME}/{filename}'
        response = await self._client.get(
            f'{YANDEX_DISK_API}/upload',
            params={'path': path, 'overwrite': 'true'},
        )
        response.raise_for_status()
        upload_url = response.json().get('href', '')
        if not upload_url:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Не удалось получить ссылку для загрузки.',
            )
        return upload_url

    async def upload_file(self, upload_url: str, content: bytes) -> None:
        """Загрузить бинарное содержимое файла по ссылке."""
        response = await self._client.put(upload_url, content=content)
        response.raise_for_status()

    async def publish_file(self, filename: str) -> str:
        """Сделать файл публичным и вернуть публичную ссылку."""
        path = f'{FOLDER_NAME}/{filename}'
        response = await self._client.put(
            f'{YANDEX_DISK_API}/publish',
            params={'path': path},
        )
        response.raise_for_status()

        response = await self._client.get(
            YANDEX_DISK_API,
            params={'path': path},
        )
        response.raise_for_status()
        public_url = response.json().get('public_url', '')
        return public_url


async def get_yandex_client() -> AsyncGenerator[YandexDiskClient, None]:
    """Dependency для получения клиента Яндекс Диска."""
    if not settings.yandex_disk_token:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail='Токен Яндекс Диска не настроен.',
        )
    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
