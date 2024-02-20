import math
from datetime import timedelta

import numpy as np
from obspy import Trace, UTCDateTime


def rms(x: np.array):
    """Calculate RMS of a np.array"""
    return np.sqrt(np.mean(x ** 2))


def snr(arrival: UTCDateTime, window_s: float, data: Trace):
    """Calculate SNR based on RMS either side of arrival"""
    noise = data.slice(arrival - timedelta(seconds=window_s), arrival)
    signal = data.slice(arrival, arrival + timedelta(seconds=window_s))
    return 10 * math.log10(rms(signal.data) / rms(noise.data))
