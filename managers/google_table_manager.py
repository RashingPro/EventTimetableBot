import pygsheets


class GoogleTableManager:
    def __init__(self, service_file: str, debug: bool = False):
        self.client = pygsheets.authorize(service_file=service_file)
        self.debug = debug
        if self.debug:
            print("<GoogleTableManager> Successfully connected to Google Sheets!")

    def get_main_table(self):
        table = self.client.open_by_key()

    def add_event(self, name: str, date: str, description: str = ''):
        ...
