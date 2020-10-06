#!/usr/bin/env python3


"""
"""
import pathlib
import threading
import logging


try:
    import sorts

    from sorts.propagator import SGP4
    from sorts.scheduler import PriorityTracking, ObservedParameters
    from sorts import SpaceObject

    import numpy as np
    from astropy.time import Time

except ImportError:
    sorts = None


def simulate_measurements(xml_request, config, logger):
    if sorts is None:
        raise RuntimeError('SORTS package not found / broken')

    eiscat3d = sorts.radars.eiscat3d

    prop_opts = dict(
        settings = dict(
            out_frame='ITRF',
        ),
    )

    objs = [
        SpaceObject(
            SGP4,
            propagator_options = prop_opts,
            a = 7200e3, 
            e = 0.0, 
            i = 75, 
            raan = 79,
            aop = 0,
            mu0 = 60,
            mjd0 = 53005.0,
            d = 1.0,
            oid = 1,
        ),
    ]

    class ObservedTracking(PriorityTracking, ObservedParameters):
        pass

    scheduler = ObservedTracking(
        radar = eiscat3d, 
        space_objects = objs,
        timeslice = 0.1, 
        allocation = 0.1*200, 
        end_time = 3600*6.0,
        epoch = Time(53005.0, format='mjd'),
        priority = [0.2, 1.0],
        logger = logger,
        collect_passes = True,
        use_pass_states = True,
    )

    scheduler.update()
    scheduler.set_measurements()

    datas = []
    for ind in range(len(objs)):
        data = scheduler.observe_passes(scheduler.passes[ind], space_object = objs[ind], snr_limit=False)
        datas.append(data)

    path = pathlib.Path(config.get('SST Server','tdm-output'))
    #CREATE TDM-XMLs here



def sensor_status(xml_request, config, logger):
    return '<status>OK</status>'