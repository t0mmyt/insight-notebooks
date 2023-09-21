import datetime as dt
from typing import NamedTuple

from obspy import Stream, UTCDateTime
from obspy.signal.polarization import flinn


class Polarization(NamedTuple):
    azimuth: float
    incident_angle: float


def polarization_azimuth(stream: Stream, offset: int):
    starttime = stream[0].meta.starttime
    data = stream.slice(
        UTCDateTime(starttime + dt.timedelta(seconds=offset)),
        UTCDateTime(starttime + dt.timedelta(seconds=offset + 10))
    )
    return Polarization(flinn(stream=data)[0], flinn(stream=data)[1])

def angle_err(a, b):
    return min(abs((a - b) % 360), abs((b - a) % 360))