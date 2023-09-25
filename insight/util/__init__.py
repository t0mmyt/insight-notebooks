from datetime import timedelta

from matplotlib.axes import Axes
from obspy import UTCDateTime
from obspy.core import Trace
from seispy.decon import RFTrace

from .download import download_file, EventDownloader, TraceFile


def rf_plot(axes: Axes, rf: RFTrace, start=10, end=40):
    sliced = trace_slice(start, end, rf)
    times = sliced.times(type="relative")
    data = sliced.data
    axes.plot(
        times,
        data,
        linewidth=0.5,
        color='k'
    )
    axes.fill_between(times, data, where=(data > 0), color='red', alpha=.3)
    axes.fill_between(times, data, where=(data < 0), color='blue', alpha=.3)


def trace_slice(start_s, end_s, trace: Trace):
    start_time = trace.stats.starttime
    return trace.slice(
        UTCDateTime(start_time + timedelta(seconds=start_s)),
        UTCDateTime(start_time + timedelta(seconds=end_s))
    )
