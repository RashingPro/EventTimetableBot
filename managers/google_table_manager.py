import datetime

import pygsheets
from managers.config_manager import ConfigManager


class GoogleTableManager:
    def __init__(self, service_file: str, debug: bool = False):
        self.debug = debug

        if self.debug:
            print("<GoogleTableManager> Connecting to Google Sheets...")
        self.client = pygsheets.authorize(service_file=service_file)
        if self.debug:
            print("<GoogleTableManager> Successfully connected to Google Sheets!")

    def get_table(self, key: str) -> pygsheets.Spreadsheet:
        table = self.client.open_by_key(key)
        return table

    def get_main_table(self) -> pygsheets.Spreadsheet:
        key = ConfigManager.get_config('config.yml')['tables']['main']
        table = self.get_table(key)
        return table

    def add_event(self, name: str, date: datetime.datetime, description: str = '', table_key: str = None):
        if self.debug:
            print('<GoogleTableManager> Adding event...')
        if table_key is None:
            table = self.get_main_table()
        else:
            table = self.get_table(table_key)
        sheet = table.add_worksheet(f'{date.strftime(f'%d.%m (%a) %H:%M')} {name}')
        sheet.update_value('A1', 'Информация')
        sheet.cell('A1').set_text_format('bold', True)
        sheet.merge_cells('A1', 'B1')
        sheet.cell('A1').set_horizontal_alignment(pygsheets.HorizontalAlignment.CENTER)

        sheet.update_value('A2', 'Название')
        sheet.update_value('B2', name)

        sheet.update_value('A3', 'Дата проведения')
        sheet.update_value('B3', date.strftime(f'%d.%m %H:%M (%A)'))

        sheet.update_value('A4', 'Описание')
        sheet.update_value('B4', description)

        drange = sheet.range('A1:B4', 'range')
        drange.update_borders(
            top=True,
            right=True,
            bottom=True,
            left=True,
            style='SOLID_MEDIUM'
        )
        drange.update_borders(inner_vertical=True, inner_horizontal=True, style='SOLID_THICK')

        sheet.adjust_column_width(1)
        sheet.adjust_column_width(2)

        sheet.update_value('D1', 'Участники')
        sheet.cell('D1').set_text_format('bold', True)
        sheet.cell('D1').set_horizontal_alignment(pygsheets.HorizontalAlignment.CENTER)

        if self.debug:
            print(f'<GoogleTableManager> Successfully added event "{name}"')
