import socket
import time
import sys
from .basestation_parser import convert_to_basestation


class BasestationReceiver:
    _aircraft = []

    def __init__(self, address, port):
        self._address = address
        self._port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        connected = False
        while not connected:
            print('Attempting to connect to {self._address}:{self._port}'.format(self=self))
            try:
                self._s.connect((self._address, self._port))
                connected = True
                print('Connection successful!\n')

            except socket.error as exception:
                print('Unable to connect to socket: {}\n'.format(exception))
                time.sleep(5)

    def disconnect(self):
        self._s.close()

    def process_beacon(self, beacon):
        if beacon.get('aprs_type') == 'position':
            basestation = convert_to_basestation(mode_s_hex=beacon.get('name')[3:9],
                                                 altitude=beacon.get('altitude'),
                                                 ground_speed=beacon.get('ground_speed'),
                                                 track=beacon.get('track'),
                                                 latitude=beacon.get('latitude'),
                                                 longitude=beacon.get('longitude'),
                                                 vertical_rate=beacon.get('climb_rate'))

            self._s.send((basestation + "\n").encode())
