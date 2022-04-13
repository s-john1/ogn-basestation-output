import logging
import socket
import time
from ogn_bs.basestation_parser import convert_to_basestation


class BasestationReceiver:
    def __init__(self, address, port, name=None, use_matched_data=True):
        if not isinstance(port, int):
            raise TypeError("port must be integer type")

        if not isinstance(use_matched_data, bool):
            raise TypeError("use_matched_data must be boolean type")

        self.logger = logging.getLogger(__name__ + '-' + name)

        self._address = address
        self._port = port
        self.name = name
        self.use_matched_data = use_matched_data
        self._s = None

    def __repr__(self):
        return f'BasestationReceiver(address={self._address}, port={self._port}, name={self.name})'

    def __str__(self):
        return f'Name: {self.name}, Address: {self._address}, Port: {self._port}'

    def connect(self):
        connected = False
        while not connected:
            self.logger.info(f'Attempting to connect to {self._address}:{self._port}')
            try:
                self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._s.connect((self._address, self._port))
                connected = True
                self.logger.info('Connection successful!')

            except socket.error:
                self.logger.exception('Unable to connect to socket')
                time.sleep(5)

    def disconnect(self):
        self._s.close()
        self.logger.info('Disconnected')

    def process_beacon(self, message):
        # Send message if it passes the filter check
        if self._filter_message(message):
            self._send_message(self.create_basestation(message))

    def _filter_message(self, beacon):
        return True

    def _send_message(self, basestation):
        self.logger.debug(f'Sending ({self._address}:{self._port}): {basestation}')

        try:
            self._s.send((basestation + "\n").encode())
        except socket.error:
            self.logger.exception('Unable to send message')
            self.disconnect()
            self.connect()

    def create_basestation(self, message):
        beacon = message.beacon
        aircraft = message.aircraft

        # Convert from m/s to fpm
        vertical_rate = beacon.get('climb_rate') * 196.85 if beacon.get('climb_rate') is not None else None

        # Convert from metres to feet
        altitude = beacon.get('altitude') * 3.2808 if beacon.get('altitude') is not None else None

        # Convert from km/h to knots
        ground_speed = beacon.get('ground_speed') / 1.852 if beacon.get('ground_speed') is not None else None

        icao = aircraft.icao if self.use_matched_data and aircraft.icao is not None else beacon.get('name')[3:9]
        registration = aircraft.registration if self.use_matched_data else None

        return convert_to_basestation(mode_s_hex=icao,
                                      altitude=altitude,
                                      ground_speed=ground_speed,
                                      track=beacon.get('track'),
                                      latitude=beacon.get('latitude'),
                                      longitude=beacon.get('longitude'),
                                      vertical_rate=vertical_rate,
                                      callsign=registration)
