import os
import requests

from common.constants import Constants

class Pushover:

    _PUSHOVER_USER = os.getenv(Constants.PUSHOVER_USER)
    _PUSHOVER_TOKEN = os.getenv(Constants.PUSHOVER_TOKEN)

    @classmethod
    def push(cls, message):
        payload = {"user": cls._PUSHOVER_USER, "token": cls._PUSHOVER_TOKEN, "message": message}
        requests.post(Constants.PUSHOVER_URL, data=payload)

if __name__ == '__main__':
    Pushover.push("HEY!!")
