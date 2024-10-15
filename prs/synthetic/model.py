from datetime import timedelta
from typing import Callable

import numpy as np

from dataclasses import dataclass
from pyraysum import prs, Model, Geometry, Control
from sklearn.metrics import mean_squared_error


@dataclass
class RandomValue:
    LowerBound: float
    UpperBound: float
    Resolution: float

    def __call__(self) -> float:
        rng = self.UpperBound - self.LowerBound
        assert rng % self.Resolution == 0
        return np.floor(np.random.random() * rng / self.Resolution) * self.Resolution + self.LowerBound


@dataclass
class Layer:
    thickness: float | Callable
    rho: float | Callable
    v_p: float | Callable
    v_s: float | Callable

    def resolve(self) -> "Layer":
        def rand_resolve(x):
            if callable(x):
                return x()
            return x

        return Layer(
            thickness=rand_resolve(self.thickness),
            rho=rand_resolve(self.rho),
            v_p=rand_resolve(self.v_p),
            v_s=rand_resolve(self.v_s),
        )


def do_synthetic(layers: [Layer]):
    model = Model(
        thickn=[l.thickness for l in layers],
        rho=[l.rho for l in layers],
        vp=[l.v_p for l in layers],
        vs=[l.v_s for l in layers],
    )
    # model.plot_profile()
    geom = Geometry(0., 0.05)  # baz = 0 deg; slow = 0.06 s/km
    rc = Control(dt=0.05, npts=1500, mults=1, rot=1)
    stream_list = prs.run(model, geom, rc, rf=True)
    # Filter and plot
    stream_list.filter('rfs', 'lowpass', freq=1., corners=2, zerophase=True)
    # stream_list.rfs[0].plot(show=False)
    start = stream_list.rfs[0][0].meta.starttime
    end = stream_list.rfs[0][0].meta.endtime
    new_start = start + timedelta(seconds=(end - start) / 2)
    new_st = stream_list.rfs[0][0].slice(new_start, end)
    # new_st.plot(show=False, type="relative")
    syn_y = new_st.data
    syn_x = np.arange(0, len(syn_y), 1) / 20
    return syn_x, syn_y, model


def t0(x, y):
    return np.interp(0, x, y)


def normalise(x, y):
    return x, y / t0(x, y)


def trim(start, end, x, y):
    return x[(x >= start) & (x <= end)], y[(x >= start) & (x <= end)]


def resample_y(x1, y1, x2, y2):
    assert len(x1) == len(y1)
    assert len(x2) == len(y2)
    # Identify the shorter trace and resample the longer one
    if len(x1) > len(x2):
        shorter, longer = (x2, y2), (x1, y1)
    else:
        shorter, longer = (x1, y1), (x2, y2)
    y = shorter[1]
    y_hat = np.interp(shorter[0], longer[0], longer[1])
    return y, y_hat


def resample(x, y, start, end, freq):
    new_x = np.linspace(start, end, (end - start) * freq + 1)
    new_y = np.interp(new_x, x, y)
    return new_x, new_y


def r2(y1, y2):
    return np.corrcoef(y1, y2)[0, 1] ** 2


def rmse(y1, y2):
    return mean_squared_error(y1, y2, squared=True)
