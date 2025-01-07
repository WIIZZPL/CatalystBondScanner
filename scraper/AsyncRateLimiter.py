from configparser import ConfigParser
from importlib import resources


class AsyncRateLimiter:
    _instance = None

    def __init__(self):
        if AsyncRateLimiter._instance is not None:
            raise Exception("Singleton violation")
        else:
            AsyncRateLimiter._instance = self
            self.config = ConfigParser()
            config_file = resources.files(__name__).joinpath('config.ini')
            self.config.read(config_file)


    @classmethod
    def get_instance(cls):
        if AsyncRateLimiter._instance is None:
            AsyncRateLimiter()
        return AsyncRateLimiter._instance