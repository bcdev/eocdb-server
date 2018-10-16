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
from .dataset_ref import DatasetRef
from .dataset_validation_result import DatasetValidationResult
from .doc_file_ref import DocFileRef
from .issue import Issue
from ...core.asserts import assert_not_empty, assert_not_none, assert_not_none_not_empty, assert_one_of


class User(Model):
    """
    The User model.
    """

    def __init__(self,
                 name: str,
                 password: str,
                 id_: int = None,
                 first_name: str = None,
                 last_name: str = None,
                 email: str = None,
                 phone: str = None,
                 permissions: int = None):
        assert_not_none(name, name='name')
        assert_not_none(password, name='password')
        self._id = id_
        self._name = name
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._password = password
        self._phone = phone
        self._permissions = permissions

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert_not_none(value, name='value')
        self._name = value

    @property
    def first_name(self) -> Optional[str]:
        return self._first_name

    @first_name.setter
    def first_name(self, value: Optional[str]):
        self._first_name = value

    @property
    def last_name(self) -> Optional[str]:
        return self._last_name

    @last_name.setter
    def last_name(self, value: Optional[str]):
        self._last_name = value

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: Optional[str]):
        self._email = value

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str):
        assert_not_none(value, name='value')
        self._password = value

    @property
    def phone(self) -> Optional[str]:
        return self._phone

    @phone.setter
    def phone(self, value: Optional[str]):
        self._phone = value

    @property
    def permissions(self) -> Optional[int]:
        return self._permissions

    @permissions.setter
    def permissions(self, value: Optional[int]):
        self._permissions = value
