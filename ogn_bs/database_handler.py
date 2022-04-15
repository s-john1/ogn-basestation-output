import json
import logging
import sys
from datetime import timedelta, datetime

import requests


class DatabaseHandler:
    DDB_URL = "https://ddb.glidernet.org/download/?j=1"
    DDB_FILE = sys.path[0] + "/ddb.json"
    DOWNLOAD_INTERVAL = timedelta(days=1)

    ICAO_FILE = sys.path[0] + "/icaos.json"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self._last_download = datetime.utcnow()

        self.download_database()
        self._ddb = self.load_database_file()

        self._icaos = self.load_icao_file()

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
                self._last_download = datetime.utcnow()
                self.logger.info("OGN DDB downloaded successfully")
        else:
            self.logger.error("Error retrieving OGN DDB - no OGN device records found")

    def load_database_file(self):
        self.logger.debug("Attempting to open database file")
        try:
            with open(self.DDB_FILE, 'r') as f:
                return json.load(f)
        except IOError:
            self.logger.exception("Unable to open database file")
        except json.JSONDecodeError:
            self.logger.exception("Unable to parse database file")
        return None

    def load_icao_file(self):
        self.logger.debug("Attempting to open ICAO file")
        try:
            with open(self.ICAO_FILE, 'r') as f:
                return json.load(f)
        except IOError:
            self.logger.exception("Unable to open ICAO file")
        except json.JSONDecodeError:
            self.logger.exception("Unable to parse ICAO file")
        return None

    def match_aircraft(self, aircraft):
        # Check if its time to re-download the database
        if self._last_download + self.DOWNLOAD_INTERVAL < datetime.utcnow():
            self.download_database()
            self.load_database_file()

        if self._ddb is None:
            self.logger.warning("Unable to match aircraft - database not loaded")
            return

        if self._icaos is None:
            self.logger.warning("Unable to match aircraft - ICAO file not loaded")
            return

        for device in self._ddb['devices']:
            if device['device_id'] == aircraft.device_id[3:9]:
                aircraft.registration = device['registration']
                aircraft.allow_tracking = device['tracked'] == 'Y'
                aircraft.competition_number = device['cn']
                break

        if aircraft.registration in self._icaos:
            aircraft.icao = self._icaos[aircraft.registration]['icao']

        return
