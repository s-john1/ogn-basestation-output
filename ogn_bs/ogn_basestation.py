from ogn.parser import parse, ParseError
from ogn.client import AprsClient
from .basestation_receiver import BasestationReceiver
from .aircraft import Aircraft


def check_message_age(aircraft, timestamp):
    if timestamp >= aircraft.time:  # Use this beacon if it is not old
        send_message = True
        aircraft.time = timestamp  # Update timestamp of aircraft
    else:  # Beacon older than previous one - don't use to avoid 'jumpy' aircraft trails
        send_message = False
        print(f'Discarding message of {aircraft} as message is old')

    return send_message


class OgnBasestation:
    def __init__(self, aprs_client, basestation_receivers):
        if not isinstance(aprs_client, AprsClient):
            raise TypeError("type AprsClient must be used")

        if not (isinstance(basestation_receivers, (list, tuple)) and
                all(isinstance(receiver, BasestationReceiver) for receiver in basestation_receivers)):
            raise TypeError("list or tuple of type BasestationReceiver must be used")

        self._aprs_client = aprs_client
        self._receivers = basestation_receivers
        self._aircraft = {}

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
            print('\nStop ogn gateway')
            self.disconnect()

    def _process_message(self, message):
        try:
            beacon = parse(message)
            print('Received {aprs_type}: {raw_message}'.format(**beacon))

            if self._validate_message(beacon):
                [receiver.process_beacon(beacon) for receiver in self._receivers]  # call process_beacon for each receiver

        except ParseError as e:
            print('Error, {}'.format(e.message))

    def _add_aircraft(self, device_id, timestamp):
        aircraft = Aircraft(device_id, timestamp)
        self._aircraft[device_id] = aircraft

        return aircraft

    def _find_aircraft(self, device_id):
        # Find out whether current aircraft object already exists
        if device_id in self._aircraft:
            return self._aircraft[device_id]
        else:
            return None

    def _validate_message(self, beacon):
        # If beacon is an aircraft position message
        if beacon.get('aprs_type') == 'position' and beacon.get('beacon_type') != 'receiver' \
                and beacon.get('beacon_type') != 'aprs_receiver' and beacon.get('beacon_type') != 'unknown':

            aircraft = self._find_aircraft(beacon.get('name'))  # Look for existing aircraft object

            if aircraft is None:  # Create new aircraft object
                aircraft = self._add_aircraft(beacon.get('name'), beacon.get('timestamp'))

            return check_message_age(aircraft, beacon.get('timestamp'))

        return False
