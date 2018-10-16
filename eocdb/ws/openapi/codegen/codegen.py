from ..model import OpenAPI
from .code import Packages
from .pyserver import CodeGenPyServer
from .pyclient import CodeGenPyClient


class CodeGen:

    @classmethod
    def gen_py_server_code(cls, openapi: OpenAPI, prod_package: str, test_package: str = None) -> Packages:
        return CodeGenPyServer.gen_code(openapi, prod_package, test_package)

    @classmethod
    def gen_py_client_code(cls, openapi: OpenAPI, prod_package: str, test_package: str = None) -> Packages:
        return CodeGenPyClient.gen_code(openapi, prod_package, test_package)


LICENSE_AND_COPYRIGHT = """The MIT License (MIT)
Copyright (c) 2018 by EUMETSAT

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
