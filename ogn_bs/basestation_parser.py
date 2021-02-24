from datetime import datetime


def convert_to_basestation(mode_s_hex, callsign=None, altitude=None, ground_speed=None, track=None,
                           latitude=None, longitude=None, vertical_rate=None, squawk=None,
                           alert=False, emergency=False, ident=False, ground=False):
    dt = datetime.now()
    date = dt.date().strftime('%Y/%m/%d')
    time = dt.time().strftime('%H:%M:%S') + '.000'

    if callsign is None:
        callsign = ''

    if altitude is None:
        altitude = ''
    else:
        altitude = round(altitude)

    if ground_speed is None:
        ground_speed = ''
    else:
        ground_speed = round(ground_speed)

    if track is None:
        track = ''
    else:
        track = round(track, 1)

    if latitude is None:
        latitude = ''
    else:
        latitude = round(latitude, 5)

    if longitude is None:
        longitude = ''
    else:
        longitude = round(longitude, 5)

    if vertical_rate is None:
        vertical_rate = ''
    else:
        vertical_rate = round(vertical_rate)

    if squawk is None:
        squawk = ''

    alert = int(alert)
    emergency = int(emergency)
    ident = int(ident)
    ground = int(ground)

    basestation = ['MSG', '3', '', '', mode_s_hex, '', date, time, date, time, callsign, altitude, ground_speed, track,
                   latitude, longitude, vertical_rate, squawk, alert, emergency, ident, ground]

    return ','.join(str(v) for v in basestation)
