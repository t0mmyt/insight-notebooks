import os

from datetime import timedelta, datetime
from typing import NamedTuple

import requests
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException
from obspy.core import stream


class TraceFile(NamedTuple):
    network: str
    station: str
    location: str
    evt_id: str
    format: str = "MSEED"

    def __str__(self):
        return f"{self.network}.{self.station}.{self.location}.{self.evt_id}".upper() + f".{self.format.lower()}"


def download_file(url: str, path: str):
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)


class EventDownloader:
    def __init__(self, data_dir, before: int, after: int):
        self.traces_dir = os.path.join(data_dir, "traces")
        self.before = before
        self.after = after
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        if not os.path.isdir(self.traces_dir):
            os.mkdir(self.traces_dir)
        self.client = Client("IRIS")

    def get_stream(
            self,
            network: str,
            station: str,
            location: str,
            channel: str,
            est_p_arrival: datetime,
            evt_id: str
    ):
        trace_file = TraceFile(network, station, location, evt_id)
        trace_file_name = os.path.join(self.traces_dir, str(trace_file))
        if not os.path.isfile(trace_file_name):
            try:
                st = self.client.get_waveforms(
                    network=network,
                    station=station,
                    location=location,
                    channel=channel,
                    starttime=UTCDateTime(est_p_arrival - timedelta(seconds=self.before)),
                    endtime=UTCDateTime(est_p_arrival + timedelta(seconds=self.after)),
                    attach_response=True,
                )
                st.write(trace_file_name, format="MSEED")
            except FDSNNoDataException:
                return None
        st = stream.read(trace_file_name)
        return st
