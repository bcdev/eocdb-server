# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import concurrent.futures
import logging
import os
from typing import Any, Dict

from eocdb.core.db.sqlite_test_db_driver import SQLiteTestDbDriver
from eocdb.ws.errors import ServiceBadRequestError
from . import __version__, __description__
from .defaults import DEFAULT_SERVER_NAME, DEFAULT_MAX_THREAD_COUNT
from .errors import WsBadRequestError
from ..core.service import ServiceRegistry

_LOG = logging.getLogger('eocdb')

Config = Dict[str, Any]

DATABASE_DRIVERS_CONFIG_NAME = "databases"


class WsContext:

    def __init__(self, base_dir=None):
        self._base_dir = os.path.abspath(base_dir or '')
        self._config = {}
        self._database_drivers = ServiceRegistry()

    @property
    def base_dir(self) -> str:
        return self._base_dir

    @property
    def config(self) -> Config:
        return self._config

    def configure(self, new_config: Config):
        old_config = self._config
        new_config = new_config or {}

        old_database_drivers = old_config.get(DATABASE_DRIVERS_CONFIG_NAME, {})
        new_database_drivers = new_config.get(DATABASE_DRIVERS_CONFIG_NAME, {})
        if old_database_drivers != new_database_drivers:
            self._database_drivers.update(new_database_drivers)

        self._config = dict(new_config)

    def dispose(self):
        self._database_drivers.dispose()

    @classmethod
    def get_app_info(cls) -> Dict:
        return dict(name=DEFAULT_SERVER_NAME,
                    description=__description__,
                    version=__version__)

    # noinspection PyMethodMayBeStatic
    def query_measurements(self, query_string: str):
        try:
            # @todo 1 tb/tb need to move this to the initialisation 2018-08-28
            self.database.connect()
            dataset = self.database.get(query_string)
            return dataset.to_dict()
        except:
            raise ServiceBadRequestError('Database error')

    # Here: add service methods, use thread_pool for concurrent requests
