import logging
import sys

import ogn_bs
import ogn


# To add custom filtering, create a class which inherits the BasestationReceiver class and override _filter_message
# like in the example which only outputs messages for aircraft with a ground speed larger than 5km/h
class FilteredReceiver(ogn_bs.BasestationReceiver):
    def _filter_message(self, message):
        beacon = message.beacon
        return beacon.get('ground_speed') is not None and beacon.get('ground_speed') > 5


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s %(name)s %(message)s')

    # By default, BasestationReceiver has no filters - all aircraft position messages are output in basestation format
    main = ogn_bs.BasestationReceiver("localhost", 30999, name="main")

    filtered = FilteredReceiver("localhost", 30998, name="filtered")

    o = ogn_bs.OgnBasestation(ogn.client.AprsClient("example", ""), [main, filtered], use_database=True)

    o.connect()
    o.start()
