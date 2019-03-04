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
from typing import Dict

from ..context import WsContext
from ..errors import WsUnauthorizedError, WsNotImplementedError
from ...core.asserts import assert_not_none
from ...core.models.user import User


# noinspection PyUnusedLocal,PyTypeChecker
def login_user(ctx: WsContext,
               username: str,
               password: str) -> Dict[str, str]:
    assert_not_none(username, name='username')
    assert_not_none(password, name='password')
    users = ctx.config.get("users")
    if not users:
        raise WsNotImplementedError("No users configured")
    if not isinstance(users, list):
        raise WsNotImplementedError("Invalid user configuration")
    for user in users:
        if not isinstance(user, dict):
            raise WsUnauthorizedError("Invalid user configuration")
    for user in users:
        if user.get("name") == username or user.get("email") == username:
            actual_password = user.get('password')
            if actual_password == password:
                user = dict(**user)
                del user['password']
                del user['email']
                del user['phone']
                return user
            else:
                break
    raise WsUnauthorizedError("Unknown username or password")


# noinspection PyUnusedLocal
def create_user(ctx: WsContext,
                user: User):
    # TODO (generated): implement operation create_user()
    raise NotImplementedError('operation create_user() not yet implemented')


# noinspection PyUnusedLocal,PyTypeChecker
def get_user_by_id(ctx: WsContext,
                   user_id: int) -> User:
    assert_not_none(user_id, name='user_id')
    # TODO (generated): implement operation get_user_by_id()
    raise NotImplementedError('operation get_user_by_id() not yet implemented')


# noinspection PyUnusedLocal
def update_user(ctx: WsContext,
                user_id: int,
                data: User):
    assert_not_none(user_id, name='user_id')
    # TODO (generated): implement operation update_user()
    raise NotImplementedError('operation update_user() not yet implemented')


# noinspection PyUnusedLocal
def delete_user(ctx: WsContext,
                id_: int):
    assert_not_none(id_, name='id_')
    # TODO (generated): implement operation delete_user()
    raise NotImplementedError('operation delete_user() not yet implemented')
