import datetime
import threading

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
        def _add_event(self, name, date, description, table_key, res):
            if self.debug:
                print(f'<GoogleTableManager> Adding event "{name}" at {date.strftime(f"%d.%m (%a) %H:%M")}...')
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
                print(f'<GoogleTableManager> Successfully added event "{name}" with id "{sheet.id}"')
            res.append(sheet.id)

        res = []
        t1 = threading.Thread(target=_add_event, args=(self, name, date, description, table_key, res))
        t1.start()
        t1.join()
        return res[0]

    def remove_event(self, event_id: int, table_key: str = None):
        def _remove_event(self: GoogleTableManager, event_id, table_key):
            if self.debug:
                print(f'<GoogleTableManager> Removing event with id "{id}"...')
            if table_key is None:
                table = self.get_main_table()
            else:
                 table = self.get_table(table_key)

            table.del_worksheet(table.worksheet('id', event_id))

            if self.debug:
                print(f'<GoogleTableManager> Successfully removed event with id "{id}"...')

        t1 = threading.Thread(target=_remove_event, args=(self, event_id, table_key))
        t1.start()

    def get_event(self, event_id: int, table_key: str = None):
        def _get_event(self: GoogleTableManager, event_id, table_key):
            if self.debug:
                print(f'<GoogleTableManager> Getting event with id "{event_id}"...')
            if table_key is not None:
                table = self.get_table(table_key)
            else:
                table = self.get_main_table()
            sheet: pygsheets.Worksheet = table.worksheet('id', event_id)
            name = sheet.cell('B2').value
            date = datetime.datetime.strptime(sheet.cell('B3').value, '%d.%m %H:%M (%A)')
            description = sheet.cell('B4').value

            members = []
            i = 2
            val = sheet.cell((i, 4)).value
            while val != '':
                _memb = val.split('/')
                members.append({'username': _memb[0], 'user_id': int(_memb[1]), 'comment': _memb[2]})
                i += 1
                val = sheet.cell((i, 4)).value

            if self.debug:
                print(f'<GoogleTableManager> Successfully got event with id "{event_id}"')

            return {'name': name, 'date': date, 'description': description, 'members': members}

        return _get_event(self, event_id, table_key)

    def book_user(self, event_id: int, user_id: int, username: str, comment: str = '', table_key: str = None):
        def _book_user(self: GoogleTableManager, event_id, user_id, username, comment, table_key):
            if self.debug:
                print(f'<GoogleTableManager> Booking user "{username}" ({user_id}) to event "{event_id}"')

            if table_key is None:
                table = self.get_main_table()
            else:
                table = self.get_table(table_key)
            sheet = table.worksheet('id', event_id)

            i = 2
            val = sheet.cell((i, 4)).value
            while val != '':
                i += 1
                val = sheet.cell((i, 4)).value

            sheet.update_value((i, 4), f'{username}/{user_id}/{comment}')

            if self.debug:
                print(f'<GoogleTableManager> Successfully booked user "{username}" ({user_id}) to event "{event_id}"')

        t1 = threading.Thread(target=_book_user, args=(self, event_id, user_id, username, comment, table_key))
        t1.start()

    def set_user_mc_nick(self, event_id: int, user_id: int, nick: str, table_key: str = None):
        def _set_user_mc_nick(self: GoogleTableManager, event_id, user_id, nick, table_key):
            if self.debug:
                print(f'<GoogleTableManager> Setting user "{user_id}" mc nick to "{nick}" in event "{event_id}"...')
            if table_key is None:
                table = self.get_main_table()
            else:
                table = self.get_table(table_key)
            sheet = table.worksheet('id', event_id)
            i = 2
            val = sheet.cell((i, 4)).value
            while val.split('/')[1] != str(user_id):
                i += 1
                val = sheet.cell((i, 4)).value
            sheet.update_value((i, 5), f'{nick}')
            if self.debug:
                print(f'<GoogleTableManager> Successfully set user "{user_id}" mc nick to "{nick}" in event "{event_id}"')

        t1 = threading.Thread(target=_set_user_mc_nick, args=(self, event_id, user_id, nick, table_key))
        t1.start()
