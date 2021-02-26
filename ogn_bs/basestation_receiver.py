import socket
import time
from .basestation_parser import convert_to_basestation
from .aircraft import Aircraft


class BasestationReceiver:
    _aircraft = []

    def __init__(self, address, port, name=None, debug=False):
        self._address = address
        self._port = port
        self.name = name
        self._s = None
        self.debug_enabled = debug

    def __repr__(self):
        return f'BasestationReceiver(address={self._address}, port={self._port}, name={self.name}, ' \
               f'aircraft={[aircraft for aircraft in self._aircraft]})'

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
        if beacon.get('aprs_type') == 'position' and beacon.get('beacon_type') != 'receiver':
            send_message = self._should_send_message(beacon)

            basestation = convert_to_basestation(mode_s_hex=beacon.get('name')[3:9],
                                                 altitude=beacon.get('altitude'),
                                                 ground_speed=beacon.get('ground_speed'),
                                                 track=beacon.get('track'),
                                                 latitude=beacon.get('latitude'),
                                                 longitude=beacon.get('longitude'),
                                                 vertical_rate=beacon.get('climb_rate'))

            if send_message:
                self._send_message(basestation)

    def _should_send_message(self, beacon):
        aircraft = self._find_aircraft(beacon.get('name'))  # Look for existing aircraft object

        if aircraft is None:  # Create new aircraft object
            aircraft = self._add_aircraft(beacon.get('name'), beacon.get('timestamp'))

        return self._check_message_age(aircraft, beacon.get('timestamp'))

    def _find_aircraft(self, device_id):
        # Find out whether current aircraft object already exists
        for aircraft in self._aircraft:
            if aircraft.device_id == device_id:
                return aircraft
        else:
            return None

    def _add_aircraft(self, device_id, timestamp):
        aircraft = Aircraft(device_id, timestamp)
        self._aircraft.append(aircraft)

        return aircraft

    def _check_message_age(self, aircraft, timestamp):
        if aircraft.is_not_older_time(timestamp):  # Use this beacon if it is not old
            send_message = True
            aircraft.time = timestamp  # Update timestamp of aircraft
        else:  # Beacon older than previous one - don't use to avoid 'jumpy' aircraft trails
            send_message = False
            self.debug(f'Not using position of {aircraft} as message is old')

        return send_message

    def _send_message(self, basestation):
        self.debug(f'Sending ({self._address}:{self._port}): {basestation}')
        self._s.send((basestation + "\n").encode())

    def debug(self, message):
        if self.debug_enabled:
            if self.name is not None:
                message = f'[{self.name}] {message}'

            print(message)
