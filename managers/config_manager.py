import yaml


class ConfigManager:
    @staticmethod
    def get_config(path: str):
        with open(f'./config/{path}') as cfg_file:
            cfg = yaml.safe_load(cfg_file)
        return cfg

    @staticmethod
    def get_local_config(path: str):
        cfg = ConfigManager.get_config(f'local/{path}')
        return cfg

    @staticmethod
    def get_local_entry(local: str, key: str):
        cfg = ConfigManager.get_local_config(local)
        entry = cfg[key]
        return entry
