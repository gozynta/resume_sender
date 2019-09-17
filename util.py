# ******************************************************************************
#  All code written for this project                                           *
#  Copyright 2013 - 2019                                                       *
#  by Gozynta, LLC.                                                            *
#  All Rights Reserved                                                         *
# ******************************************************************************
import os
import shelve

import click


def load_cache() -> shelve.Shelf:
    cache_dir = click.get_app_dir('Gozynta', roaming=False)

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    return shelve.open(os.path.join(cache_dir, 'applicant_cache'))
