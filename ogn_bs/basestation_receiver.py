import socket
import time
from .basestation_parser import convert_to_basestation


def create_basestation(beacon):
    return convert_to_basestation(mode_s_hex=beacon.get('name')[3:9],
                                  altitude=beacon.get('altitude'),
                                  ground_speed=beacon.get('ground_speed'),
                                  track=beacon.get('track'),
                                  latitude=beacon.get('latitude'),
                                  longitude=beacon.get('longitude'),
                                  vertical_rate=beacon.get('climb_rate'))


class BasestationReceiver:
    def __init__(self, address, port, name=None, debug=False):
        self._address = address
        self._port = port
        self.name = name
        self._s = None
        self.debug_enabled = debug

    def __repr__(self):
        return f'BasestationReceiver(address={self._address}, port={self._port}, name={self.name})'

    def __str__(self):
        return f'Name: {self.name}, Address: {self._address}, Port: {self._port}'

    def connect(self):
        connected = False
        while not connected:
            self.debug(f'Attempting to connect to {self._address}:{self._port}')
            try:
                self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._s.connect((self._address, self._port))
                connected = True
                self.debug('Connection successful!\n')

            except socket.error as exception:
                self.debug(f'Unable to connect to socket: {exception}\n')
                time.sleep(5)

    def disconnect(self):
        self._s.close()

    def process_beacon(self, beacon):
        # Send message if it passes the filter check
        if self._filter_message(beacon):
            self._send_message(create_basestation(beacon))

    def _filter_message(self, beacon):
        return True

    def _send_message(self, basestation):
        self.debug(f'Sending ({self._address}:{self._port}): {basestation}')
        self._s.send((basestation + "\n").encode())

    def debug(self, message):
        if self.debug_enabled:
            if self.name is not None:
                message = f'[{self.name}] {message}'

            print(message)
