import re
from datetime import datetime


class Aircraft:
    _icao = None
    _registration = None

    def __init__(self, device_id, current_time):
        self.device_id = device_id
        self._check_time_instance(current_time)
        self._time = current_time

    def __repr__(self):
        return f'Aircraft(device_id={self.device_id}, time={repr(self._time)}, icao={self._icao},' \
               f'registration={self._registration})'

    def __str__(self):
        return f'Aircraft: {self.device_id}, Time: {self._time}, ICAO: {self._icao}, Registration: {self._registration}'

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._check_time_instance(value)
        self._time = value

    @property
    def icao(self):
        return self._icao

    @icao.setter
    def icao(self, value):
        if not re.match("^([A-Fa-f0-9]{6})$", value):
            raise TypeError("ICAO is not in 6 digit hex format")

        self._icao = value

    @property
    def registration(self):
        return self._registration

    @registration.setter
    def registration(self, value):
        self._registration = value

    @staticmethod
    def _check_time_instance(value):
        if not isinstance(value, datetime):
            raise TypeError("A datetime object must be used")
