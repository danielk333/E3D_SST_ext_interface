#!/usr/bin/env python3


"""
"""
import pathlib
import threading
import logging
import io

try:
    import numpy as np
    from astropy.time import Time, TimeDelta
except ImportError:
    np = None
    Time, TimeDelta = (None, None)

try:
    import sorts
except ImportError:
    sorts = None

from config import ROOT

if sorts is not None:
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
    EPOCH = pop.get_object(0).epoch
else:
    pop = None
    radar = None
    EPOCH = None


def simulate_measurements(object_index, samples=10, max_h = 24.0, noise=False):
    if sorts is None:
        raise RuntimeError('SORTS package not found / broken')

    if noise:
        raise NotImplementedError('Fix this')

    obj = pop.get_object(object_index)

    t = np.arange(0, max_h*3600.0, 10.0)

    states = obj.get_state(t)
    passes = radar.find_passes(t, states, cache_data = True)


    class ObservedTracking(sorts.scheduler.StaticList, sorts.scheduler.ObservedParameters):
        pass

    controllers = []
    for ps in passes[0][0]:
        _t = np.linspace(ps.start(), ps.end(), num=samples)
        _t = np.round(_t*10)/10.0
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
        epoch = EPOCH,
        logger = logging,
    )

    data = scheduler.observe_passes(passes, space_object = obj, snr_limit=True)


    tdms = []
    for rxi in range(len(data[0])):
        for d in data[0][rxi]:
            t_vec = EPOCH + TimeDelta(d['t'], format='sec')

            meta = dict(
                COMMENT = 'Generated from E3D External interface prototype',
                TIME_SYSTEM = 'UTC',
                START_TIME = t_vec.min().CCSDS_epoch,
                STOP_TIME = t_vec.max().CCSDS_epoch,
                PARTICIPANT_1 = f'EISCAT 3D TX {0}',
                PARTICIPANT_2 = f'Catalog object id {obj.oid}',
                PARTICIPANT_3 = f'EISCAT 3D RX {rxi}',
                MODE = 'SEQUENTIAL',
                PATH = '1,2,3',
                TRANSMIT_BAND = 'VHF',
                RECEIVE_BAND = 'VHF',
                TIMETAG_REF = 'TRANSMIT',
                INTEGRATION_INTERVAL = 0.1,
                INTEGRATION_REF = 'END',
                RANGE_UNITS = 'km',
            )

            data_tdm = np.empty(
                (len(d['t']),), 
                dtype=[
                    ('EPOCH', 'datetime64[ns]'),
                    ('RANGE', 'f8'),
                    ('DOPPLER_INSTANTANEOUS', 'f8'),
                ],
            )
            data_tdm['RANGE'] = d['range']*1e-3
            data_tdm['DOPPLER_INSTANTANEOUS'] = d['range_rate']*1e-3
            data_tdm['EPOCH'] = t_vec.datetime64

            stream = io.StringIO()

            sorts.io.ccsds.write_xml_tdm(data_tdm, meta, file=stream)

            tdms.append(stream.getvalue())

            stream.close()

    return tdms




def simulate_scan(t0, t1, noise=False):
    if sorts is None:
        raise RuntimeError('SORTS package not found / broken')

    if noise:
        raise NotImplementedError('Fix this')

    t = np.arange(t0, t1, 0.1)
    t_samp = np.arange(t0, t1, 10.0)

    class ObservedScanning(sorts.scheduler.StaticList, sorts.scheduler.ObservedParameters):
        pass

    scan = sorts.radar.scans.Fence(azimuth=90, num=40, dwell=0.1, min_elevation=30)
    scanner = sorts.controller.Scanner(
        radar, 
        scan,
        t=t, 
        t_slice=0.1,
        logger = logging,
    )

    scheduler = ObservedScanning(
        radar = radar, 
        controllers = [scanner], 
        epoch = EPOCH,
        logger = logging,
    )

    tdms = []
    for obj in pop:
        states = obj.get_state(t_samp)
        passes = radar.find_passes(t_samp, states, cache_data = True)

        data = scheduler.observe_passes(passes, space_object = obj, snr_limit=True)

        tdms.append([])
        for rxi in range(len(data[0])):
            if len(data[0][rxi]) == 0:
                continue

            meta = dict(
                COMMENT = 'Generated from E3D External interface prototype',
                PARTICIPANT_1 = f'EISCAT 3D TX {0}',
                PARTICIPANT_2 = f'Catalog object id {obj.oid}',
                PARTICIPANT_3 = f'EISCAT 3D RX {rxi}',
            )


            for d in data[0][rxi]:
                if d is None:
                    continue
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
                data_tdm['EPOCH'] = (EPOCH + d['t']).datetime64

                stream = io.StringIO()

                sorts.io.ccsds.write_xml_tdm(data_tdm, meta, file=stream)

                tdms[-1].append(stream.getvalue())

                stream.close()

    return tdms
