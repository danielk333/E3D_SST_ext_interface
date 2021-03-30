#!/usr/bin/env python3


"""
"""
import pathlib
import threading
import logging
import io

try:
    import numpy as np
except ImportError:
    np = None

try:
    import sorts
except ImportError:
    sorts = None

from config import ROOT

def simulate_measurements(object_index, samples=10, max_h = 24.0, noise=False):
    if sorts is None:
        raise RuntimeError('SORTS package not found / broken')

    if noise:
        raise NotImplementedError('Fix this')

    pop_cache_path = ROOT / 'data' / 'sample_population.h5'

    radar = sorts.radars.eiscat3d_interp

    pop_kw = dict(
        propagator = sorts.propagator.SGP4,
        propagator_options = dict(
            settings = dict(
                in_frame='TEME',
                out_frame='ITRS',
            ),
        ),
    )
    pop = sorts.Population.load(pop_cache_path, **pop_kw)

    obj = pop.get_object(object_index)

    t = np.arange(0, max_h*3600.0, 10.0)

    states = obj.get_state(t)
    passes = radar.find_passes(t, states, cache_data = True)


    class ObservedTracking(sorts.scheduler.StaticList, sorts.scheduler.ObservedParameters):
        pass

    controllers = []
    for ps in passes[0][0]:
        _t = np.linspace(ps.start(), ps.end(), num=samples)
        _st = obj.get_state(_t)

        track = sorts.controller.Tracker(
            radar=radar, 
            t=_t, 
            ecefs=_st[:3,:], 
            dwell = 0.1, 
            logger = logging,
        )
        controllers.append(track)


    scheduler = ObservedTracking(
        radar = radar, 
        controllers = controllers, 
        epoch = obj.epoch,
        logger = logging,
    )

    data = scheduler.observe_passes(passes, space_object = obj, snr_limit=True)


    tdms = []
    for rxi in range(len(data[0])):

        meta = dict(
            COMMENT = 'Generated from E3D External interface prototype',
            PARTICIPANT_1 = f'EISCAT 3D TX {0}',
            PARTICIPANT_2 = f'Catalog object id {obj.oid}',
            PARTICIPANT_3 = f'EISCAT 3D RX {rxi}',
        )

        for d in data[0][rxi]:
            data_tdm = np.empty(
                (len(d['t']),), 
                dtype=[
                    ('EPOCH', 'datetime64[ns]'),
                    ('RANGE', 'f8'),
                    ('DOPPLER_INSTANTANEOUS', 'f8'),
                ],
            )
            data_tdm['RANGE'] = d['range']
            data_tdm['DOPPLER_INSTANTANEOUS'] = d['range_rate']
            data_tdm['EPOCH'] = (obj.epoch + d['t']).datetime64

            stream = io.StringIO()

            sorts.io.ccsds.write_xml_tdm(data_tdm, meta, file=stream)

            tdms.append(stream.getvalue())

            stream.close()

    return tdms
