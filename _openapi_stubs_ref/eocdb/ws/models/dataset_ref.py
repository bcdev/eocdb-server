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
from .dataset import Dataset
from .dataset_query import DatasetQuery
from .dataset_query_result import DatasetQueryResult
from .dataset_validation_result import DatasetValidationResult
from .doc_file_ref import DocFileRef
from .issue import Issue
from .user import User
from ...core.asserts import assert_not_empty, assert_not_none, assert_not_none_not_empty, assert_one_of


class DatasetRef(Model):
    """
    The DatasetRef model.
    """

    def __init__(self,
                 id_: str,
                 bucket: Bucket,
                 name: str):
        assert_not_none(id_, name='id_')
        assert_not_none(bucket, name='bucket')
        assert_not_none(name, name='name')
        self._id = id_
        self._bucket = bucket
        self._name = name

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        assert_not_none(value, name='value')
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
