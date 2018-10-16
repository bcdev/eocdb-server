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


from typing import Dict, List

from ..context import WsContext
from ..models.bucket import Bucket
from ..models.dataset import Dataset
from ..models.dataset_query import DatasetQuery
from ..models.dataset_query_result import DatasetQueryResult
from ..models.dataset_ref import DatasetRef
from ..models.dataset_validation_result import DatasetValidationResult
from ..models.doc_file_ref import DocFileRef
from ..models.issue import Issue
from ..models.user import User
from ...core.asserts import assert_not_empty, assert_not_none, assert_not_none_not_empty, assert_one_of


# noinspection PyUnusedLocal
def get_store_info(ctx: WsContext) -> Dict:
    # TODO (generated): implement operation get_store_info()
    raise NotImplementedError('operation get_store_info() not yet implemented')


# noinspection PyUnusedLocal
def upload_store_files(ctx: WsContext,
                       data: Dict):
    # TODO (generated): implement operation upload_store_files()
    raise NotImplementedError('operation upload_store_files() not yet implemented')


# noinspection PyUnusedLocal
def download_store_files(ctx: WsContext,
                         expr: str = None,
                         region: List[float] = None,
                         time: List[str] = None,
                         wdepth: List[float] = None,
                         mtype: str = 'all',
                         wlmode: str = 'all',
                         shallow: str = 'no',
                         pmode: str = 'contains',
                         pgroup: List[str] = None,
                         pname: List[str] = None,
                         docs: bool = False) -> str:
    assert_one_of(wlmode, ['all', 'multispectral', 'hyperspectral'], name='wlmode')
    assert_one_of(shallow, ['no', 'yes', 'exclusively'], name='shallow')
    assert_one_of(pmode, ['contains', 'same_cruise', 'dont_apply'], name='pmode')
    # TODO (generated): implement operation download_store_files()
    raise NotImplementedError('operation download_store_files() not yet implemented')
