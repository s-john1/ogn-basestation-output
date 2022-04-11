import json
import logging
import sys

import requests


class DatabaseHandler:
    DDB_URL = "https://ddb.glidernet.org/download/?j=1"
    DDB_FILE = sys.path[0] + "/ddb.json"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.download_database()
        self._ddb = self._load_database_file()

        # TODO: automatically re-download database every day

    def download_database(self):
        data = None

        self.logger.info("Attempting to download OGN DDB")
        try:
            r = requests.get(self.DDB_URL)
            data = r.json()
        except requests.exceptions.RequestException:
            self.logger.exception("Error retrieving OGN DDB")
            return
        except json.decoder.JSONDecodeError:
            self.logger.exception("Error retrieving OGN DDB - JSON response not valid")
            return

        if 'devices' in data and len(data['devices']) > 0:
            with open(self.DDB_FILE, 'w') as f:
                json.dump(data, f)
                self.logger.info("OGN DDB downloaded successfully")
        else:
            self.logger.error("Error retrieving OGN DDB - no OGN device records found")

    def _load_database_file(self):
        self.logger.debug("Attempting to open database file")
        try:
            with open(self.DDB_FILE, 'r') as f:
                return json.load(f)
        except IOError:
            self.logger.exception("Unable to open database file")
        except json.JSONDecodeError:
            self.logger.exception("Unable to parse database file")
        return None

    def match_aircraft(self, aircraft):
        if self._ddb is None:
            self.logger.warning("Unable to match aircraft - database not loaded")
            return

        for device in self._ddb['devices']:
            if device['device_id'] == aircraft.device_id[3:9]:
                aircraft.registration = device['registration']
                aircraft.allow_tracking = device['tracked'] == 'Y'
                return
