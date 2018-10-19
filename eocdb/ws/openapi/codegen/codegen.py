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

