import os.path
from typing import NamedTuple

import requests
import pandas as pd
import xml.etree.ElementTree as et

from dateutil.parser import isoparse


class CatalogDFs(NamedTuple):
    events: pd.DataFrame


class InsightCatalog:
    ns = {
        "bed": "http://quakeml.org/xmlns/bed/1.2",
        "q": "http://quakeml.org/xmlns/quakeml",
        "mars": "http://quakeml.org/xmlns/bed/1.2/mars",
        "mq": "http://quakeml.org/xmlns/marsquake/1.0",
        "sst": "http://quakeml.org/xmlns/singlestation/1.0"
    }

    def __init__(self, url: str, data_dir: str):
        self.data_dir = data_dir
        self.url = url
        self.filename = os.path.join(data_dir, url[url.rfind("/") + 1:])

    def parse(self):
        self._download_catalog()
        xtree = et.parse(self.filename)
        xroot = xtree.getroot()

        for node in xroot:
            if node.tag == "{http://quakeml.org/xmlns/bed/1.2}eventParameters":
                events = self._events(node)
            elif node.tag == "{http://quakeml.org/xmlns/singlestation/1.0}singleStationParameters":
                pass
            elif node.tag == "{http://quakeml.org/xmlns/marsquake/1.0}marsquakeParameters":
                pass

        return CatalogDFs(
            events=events,
        )

    def _download_catalog(self):
        if os.path.exists(self.filename):
            return
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        with requests.get(self.url, stream=True) as resp:
            resp.raise_for_status()
            with open(self.filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)

    def _events(self, node: et.Element):
        rows = []
        for event in node.iterfind("bed:event", self.ns):
            evt_id = event.get("publicID")
            row = {"id": evt_id[evt_id.rfind("/") + 1:]}
            for desc in event.findall("bed:description", self.ns):
                desc_text = desc.find("bed:text", self.ns).text
                desc_type = desc.find("bed:type", self.ns).text
                row[desc_type] = desc_text

            origin = event.find("bed:origin", self.ns)
            if origin is not None:
                evt_time = origin.find("bed:time", self.ns)
                if evt_time is not None:
                    row["time"] = evt_time.find("bed:value", self.ns).text

                quality = origin.find("mars:locationQuality", self.ns)
                if quality is not None:
                    row["quality"] = quality.text[-1]

                for arrival in origin.iterfind("bed:arrival", self.ns):
                    phase = arrival.find("bed:phase", self.ns).text
                    if phase == "start":
                        azimuth = arrival.find("bed:azimuth", self.ns)
                        if azimuth is not None:
                            row["mqs_azimuth"] = float(azimuth.text)
                        distance = arrival.find("bed:distance", self.ns)
                        if distance is not None:
                            row["mqs_distance"] = float(distance.text)

            for pick in event.iterfind("bed:pick", self.ns):
                phase_hint = pick.find("bed:phaseHint", self.ns).text
                if phase_hint == "P":
                    row["p_arrival"] = isoparse(pick.find("bed:time", self.ns).find("bed:value", self.ns).text)
                    break

            for pick in event.iterfind("bed:pick", self.ns):
                phase_hint = pick.find("bed:phaseHint", self.ns).text
                if phase_hint == "PP":
                    row["pp_arrival"] = isoparse(pick.find("bed:time", self.ns).find("bed:value", self.ns).text)
                    break

            for mag in event.iterfind("bed:magnitude", self.ns):
                if mag.find("bed:type", self.ns).text == "MW":
                    row["M_w"] = mag.find("bed:mag", self.ns).find("bed:value", self.ns).text
                    break

            rows.append(row)
        return pd.DataFrame(rows)