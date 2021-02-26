from datetime import datetime


class Aircraft:
    _time = None

    def __init__(self, device_id, current_time):
        self.device_id = device_id
        self._check_time_instance(current_time)
        self._time = current_time

    def __repr__(self):
        return f'Aircraft(device_id={self.device_id})'

    def __str__(self):
        return f'Aircraft: {self.device_id}'

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._check_time_instance(value)
        self._time = value

    @staticmethod
    def _check_time_instance(value):
        if not isinstance(value, datetime):
            raise TypeError("A datetime object must be used")

    def is_not_older_time(self, time):
        return time >= self._time

