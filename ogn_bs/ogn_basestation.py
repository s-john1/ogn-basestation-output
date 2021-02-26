from ogn.parser import parse, ParseError
from ogn.client import AprsClient
from .basestation_receiver import BasestationReceiver


class OgnBasestation:
    def __init__(self, aprs_client, basestation_receivers):
        if not isinstance(aprs_client, AprsClient):
            raise TypeError("type AprsClient must be used")

        if not (isinstance(basestation_receivers, (list, tuple)) and
                all(isinstance(receiver, BasestationReceiver) for receiver in basestation_receivers)):
            raise TypeError("list or tuple of type BasestationReceiver must be used")

        self._aprs_client = aprs_client
        self._receivers = basestation_receivers

    def __repr__(self):
        return f'OgnBasestation(aprs_client={repr(self._aprs_client)}, ' \
               f'receivers={[repr(receiver) for receiver in self._receivers]})'

    def connect(self):
        self._aprs_client.connect()
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

            [receiver.process_beacon(beacon) for receiver in self._receivers]  # call process_beacon for each receiver

        except ParseError as e:
            print('Error, {}'.format(e.message))
