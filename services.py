#!/usr/bin/env python3


"""
"""

import sorts


def simulate_measurements(xml_request, config):
    return f'HEYYYWO: sorts version = {sorts.__version__}'


def check_status(xml_request, config):
    if config['__on']:
        return None
    else:
        raise Exception('we are offline')