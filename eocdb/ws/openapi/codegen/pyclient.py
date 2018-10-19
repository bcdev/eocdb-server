from .code import Packages
from .pybase import CodeGenPy
from ..model import OpenAPI


class CodeGenPyClient(CodeGenPy):
    def __init__(self, openapi: OpenAPI, prod_package: str, test_package: str = None):
        super().__init__(openapi)
        self._prod_package = prod_package
        self._test_package = test_package

    @classmethod
    def gen_code(cls, openapi: OpenAPI, prod_package: str, test_package: str = None) -> Packages:
        code_gen = CodeGenPyClient(openapi, prod_package, test_package=test_package)
        packages = dict()
        code_gen._gen_functions(packages)
        code_gen._gen_models(packages)
        if test_package:
            code_gen._gen_functions_tests(packages)
            code_gen._gen_models_tests(packages)
        return packages

    def _gen_models(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for schema_name, schema in self._openapi.components.schemas.items():
            self._gen_model_code(schema_name, schema, modules)
        packages[self._prod_package + ".models"] = modules

    def _gen_models_tests(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for schema_name, schema in self._openapi.components.schemas.items():
            self._gen_model_tests_code(schema_name, schema, modules)
        packages[self._test_package + ".models"] = modules

    def _gen_functions(self, packages):
        # TODO by forman: - implement me
        raise NotImplementedError()

    def _gen_functions_tests(self, packages):
        # TODO by forman: - implement me
        raise NotImplementedError()

