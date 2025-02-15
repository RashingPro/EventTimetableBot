import datetime
import threading

from managers import google_table_manager


def add_event(name: str, date: datetime.datetime, description: str = ''):
    t1 = threading.Thread(target=g_table.add_event, args=(name, date, description))
    t1.start()


if __name__ == '__main__':
    g_table = google_table_manager.GoogleTableManager('./auth.json', debug=True)

