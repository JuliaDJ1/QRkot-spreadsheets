from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import List

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient
from app.models.charity_project import CharityProject

SECONDS_IN_DAY = 86400
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60


def format_time_delta(delta: timedelta) -> str:
    """Форматировать timedelta в читаемую строку."""
    total_seconds = int(delta.total_seconds())
    days = total_seconds // SECONDS_IN_DAY
    hours = (total_seconds % SECONDS_IN_DAY) // SECONDS_IN_HOUR
    minutes = (total_seconds % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE

    if days > 0:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    client: YandexDiskClient,
    projects: List[CharityProject],
) -> str:
    """Создать Excel-отчёт и загрузить на Яндекс Диск."""
    now = datetime.now(timezone.utc)
    filename = f'report_{now.strftime(settings.report_format)}.xlsx'

    upload_url = await client.create_excel_file(filename)

    with BytesIO() as output:
        with xlsxwriter.Workbook(output, {'in_memory': True}) as workbook:
            worksheet = workbook.add_worksheet('Отчёт')

            bold = workbook.add_format({'bold': True})
            header_fmt = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1,
            })
            cell_fmt = workbook.add_format({'border': 1})

            worksheet.write(
                0, 0,
                f'Отчёт от {now.strftime("%d.%m.%Y %H:%M")}',
                bold,
            )

            headers = ['Название проекта', 'Время сбора', 'Описание']
            for col, header in enumerate(headers):
                worksheet.write(1, col, header, header_fmt)

            for row, project in enumerate(projects, start=2):
                if project.close_date and project.create_date:
                    delta = project.close_date - project.create_date
                    time_str = format_time_delta(delta)
                else:
                    time_str = '—'

                worksheet.write(row, 0, project.name, cell_fmt)
                worksheet.write(row, 1, time_str, cell_fmt)
                worksheet.write(row, 2, project.description, cell_fmt)

            total_row = len(projects) + 2
            worksheet.write(
                total_row, 0,
                f'Итого проектов: {len(projects)}',
                bold,
            )

        output.seek(0)
        file_content = output.read()

    await client.upload_file(upload_url, file_content)
    public_url = await client.publish_file(filename)

    return public_url
