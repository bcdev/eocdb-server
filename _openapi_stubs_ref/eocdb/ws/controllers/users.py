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
def create_user(ctx: WsContext,
                data: User):
    # TODO (generated): implement operation create_user()
    raise NotImplementedError('operation create_user() not yet implemented')


# noinspection PyUnusedLocal
def login_user(ctx: WsContext,
               username: str,
               password: str) -> str:
    assert_not_none(username, name='username')
    assert_not_none(password, name='password')
    # TODO (generated): implement operation login_user()
    raise NotImplementedError('operation login_user() not yet implemented')


# noinspection PyUnusedLocal
def logout_user(ctx: WsContext):
    # TODO (generated): implement operation logout_user()
    raise NotImplementedError('operation logout_user() not yet implemented')


# noinspection PyUnusedLocal
def get_user_by_id(ctx: WsContext,
                   id_: int) -> User:
    assert_not_none(id_, name='id_')
    # TODO (generated): implement operation get_user_by_id()
    raise NotImplementedError('operation get_user_by_id() not yet implemented')


# noinspection PyUnusedLocal
def update_user(ctx: WsContext,
                id_: int,
                data: User):
    assert_not_none(id_, name='id_')
    # TODO (generated): implement operation update_user()
    raise NotImplementedError('operation update_user() not yet implemented')


# noinspection PyUnusedLocal
def delete_user(ctx: WsContext,
                id_: int):
    assert_not_none(id_, name='id_')
    # TODO (generated): implement operation delete_user()
    raise NotImplementedError('operation delete_user() not yet implemented')
