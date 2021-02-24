from ogn.parser import parse, ParseError


class OgnBasestation:
    def __init__(self, ogn_client, basestation_receivers):
        self._ogn_client = ogn_client
        self._receivers = basestation_receivers

    def connect(self):
        self._ogn_client.connect()
        [receiver.connect() for receiver in self._receivers]  # connect each receiver

    def disconnect(self):
        self._ogn_client.disconnect()
        [receiver.disconnect() for receiver in self._receivers]  # disconnect each receiver

    def start(self):
        try:
            self._ogn_client.run(callback=self._process_message, autoreconnect=True)
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
