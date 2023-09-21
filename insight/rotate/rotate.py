from obspy import Stream, Trace
from obspy.core import Stats
from obspy.signal.rotate import rotate2zne


def rotate_zne(
        stream: Stream,
        orientations: dict,
        band: str = "B",
        instrument: str = "H",
        components: str = "UVW"):
    rotate_params = (
        (stream.select(channel=ch)[0].data, orientations[ch]["azimuth"], orientations[ch]["dip"])
        for ch in [f"{band}{instrument}{c}" for c in components]
    )
    zne = rotate2zne(*(i for j in rotate_params for i in j))

    def stats(ch: str) -> dict:
        t: Stats = stream.traces[0].stats.copy()
        t["channel"] = t["channel"][:-1] + ch
        return t

    return Stream(
        traces=[
            Trace(data=zne[i], header=stats("ZNE"[i]))
            for i in range(3)
        ]
    )
