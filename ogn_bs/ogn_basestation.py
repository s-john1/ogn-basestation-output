import logging
from collections import namedtuple
from datetime import datetime, timedelta

from ogn.parser import parse
from ogn.client import AprsClient
from ogn_bs.basestation_receiver import BasestationReceiver
from ogn_bs.aircraft import Aircraft
from ogn_bs.database_handler import DatabaseHandler


class OgnBasestation:
    AIRCRAFT_TIMEOUT = timedelta(minutes=10)
    REMOVE_CHECK_INTERVAL = timedelta(minutes=5)

    def __init__(self, aprs_client, basestation_receivers, use_database=True):
        self.logger = logging.getLogger(__name__)

        if not isinstance(aprs_client, AprsClient):
            raise TypeError("type AprsClient must be used")

        if not (isinstance(basestation_receivers, (list, tuple)) and
                all(isinstance(receiver, BasestationReceiver) for receiver in basestation_receivers)):
            raise TypeError("list or tuple of type BasestationReceiver must be used")

        if not isinstance(use_database, bool):
            raise TypeError("use_database must be boolean type")

        self._aprs_client = aprs_client
        self._receivers = basestation_receivers
        self._aircraft = {}
        self._last_remove_check = datetime.utcnow()
        self._use_database = use_database
        self._ddb = None

        if use_database:
            self._ddb = DatabaseHandler()

    def __repr__(self):
        return f'OgnBasestation(aprs_client={repr(self._aprs_client)}, ' \
               f'receivers={[repr(receiver) for receiver in self._receivers]},' \
               f'aircraft={[aircraft for aircraft in self._aircraft]})'

    def connect(self):
        self._aprs_client.connect(retries=float('inf'))
        [receiver.connect() for receiver in self._receivers]  # connect each receiver

    def disconnect(self):
        self._aprs_client.disconnect()
        [receiver.disconnect() for receiver in self._receivers]  # disconnect each receiver

    def start(self):
        try:
            self._aprs_client.run(callback=self._process_message, autoreconnect=True)
        except KeyboardInterrupt:
            self.logger.info('Stopping program')
            self.disconnect()

    def _process_message(self, message):
        # Check if its time to remove old aircraft objects
        if self._last_remove_check + self.REMOVE_CHECK_INTERVAL < datetime.utcnow():
            self._remove_aircraft()
            self._last_remove_check = datetime.utcnow()

        try:
            beacon = parse(message)
        except Exception:
            self.logger.exception('Error parsing beacon')
            return

        self.logger.debug('Received {aprs_type}: {raw_message}'.format(**beacon))

        message = self._validate_message(beacon)
        if message is not False:
            [receiver.process_beacon(message) for receiver in self._receivers]  # call process_beacon for each receiver

    def _add_aircraft(self, device_id, timestamp):
        aircraft = Aircraft(device_id, timestamp)
        self._aircraft[device_id] = aircraft

        if self._use_database:
            self._ddb.match_aircraft(aircraft)

        return aircraft

    def _remove_aircraft(self):
        for aircraft in list(self._aircraft):
            if self._aircraft[aircraft].time < datetime.utcnow() - self.AIRCRAFT_TIMEOUT:
                self.logger.debug("Removing inactive aircraft:", repr(aircraft))
                del self._aircraft[aircraft]

    def _find_aircraft(self, device_id):
        # Find out whether current aircraft object already exists
        if device_id in self._aircraft:
            return self._aircraft[device_id]
        else:
            return None

    def _validate_message(self, beacon):
        # Discard beacons that are not aircraft position messages
        if not(beacon.get('aprs_type') == 'position' and beacon.get('beacon_type') != 'receiver'
               and beacon.get('beacon_type') != 'aprs_receiver' and beacon.get('beacon_type') != 'unknown'):
            return False

        aircraft = self._find_aircraft(beacon.get('name'))  # Look for existing aircraft object

        if aircraft is None:  # Create new aircraft object
            aircraft = self._add_aircraft(beacon.get('name'), beacon.get('timestamp'))

        # Discard messages from blocked aircraft, and messages which are old
        if not aircraft.allow_tracking or not self.check_message_age(aircraft, beacon.get('timestamp')):
            return False

        message = namedtuple('Message', ['beacon', 'aircraft'])
        return message(beacon, aircraft)

    def check_message_age(self, aircraft, timestamp):
        if timestamp >= aircraft.time:  # Use this beacon if it is not old
            send_message = True
            aircraft.time = timestamp  # Update timestamp of aircraft
        else:  # Beacon older than previous one - don't use to avoid 'jumpy' aircraft trails
            send_message = False
            self.logger.debug(f'Discarding message of {repr(aircraft)} as message is old')

        return send_message
