import datetime

from managers import google_table_manager


if __name__ == '__main__':
    g_table = google_table_manager.GoogleTableManager('./auth.json', debug=True)
    g_table.add_event('тесмтовый', datetime.datetime.now(), 'тето')
