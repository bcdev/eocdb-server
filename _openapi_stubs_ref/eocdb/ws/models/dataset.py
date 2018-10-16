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


from typing import Dict, List, Optional

from ..model import Model
from .bucket import Bucket
from .dataset_query import DatasetQuery
from .dataset_query_result import DatasetQueryResult
from .dataset_ref import DatasetRef
from .dataset_validation_result import DatasetValidationResult
from .doc_file_ref import DocFileRef
from .issue import Issue
from .user import User
from ...core.asserts import assert_not_empty, assert_not_none, assert_not_none_not_empty, assert_one_of

DATASET_STATUS_NEW = 'new'
DATASET_STATUS_VALIDATING = 'validating'
DATASET_STATUS_AVAILABLE = 'available'
DATASET_STATUS_HIDDEN = 'hidden'


class Dataset(Model):
    """
    The Dataset model.
    """

    def __init__(self,
                 bucket: Bucket,
                 name: str,
                 status: str,
                 metadata: Dict,
                 records: List[List[float]],
                 id_: str = None):
        assert_not_none(bucket, name='bucket')
        assert_not_none(name, name='name')
        assert_not_none(status, name='status')
        assert_one_of(status, ['new', 'validating', 'available', 'hidden'], name='status')
        assert_not_none(metadata, name='metadata')
        assert_not_none(records, name='records')
        self._id = id_
        self._bucket = bucket
        self._name = name
        self._status = status
        self._metadata = metadata
        self._records = records

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]):
        self._id = value

    @property
    def bucket(self) -> Bucket:
        return self._bucket

    @bucket.setter
    def bucket(self, value: Bucket):
        assert_not_none(value, name='value')
        self._bucket = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert_not_none(value, name='value')
        self._name = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        assert_not_none(value, name='value')
        assert_one_of(value, ['new', 'validating', 'available', 'hidden'], name='value')
        self._status = value

    @property
    def metadata(self) -> Dict:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict):
        assert_not_none(value, name='value')
        self._metadata = value

    @property
    def records(self) -> List[List[float]]:
        return self._records

    @records.setter
    def records(self, value: List[List[float]]):
        assert_not_none(value, name='value')
        self._records = value
