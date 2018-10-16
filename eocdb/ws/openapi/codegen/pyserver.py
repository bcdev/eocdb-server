from typing import Dict

from .code import Code, Packages
from .pybase import CodeGenPy
from ..model import OpenAPI, Operation
from ....core import UNDEFINED


class CodeGenPyServer(CodeGenPy):
    def __init__(self, openapi: OpenAPI, prod_package: str, test_package: str = None):
        super().__init__(openapi)
        self._prod_package = prod_package
        self._test_package = test_package

    @classmethod
    def gen_code(cls, openapi: OpenAPI, prod_package: str, test_package: str = None) -> Packages:
        code_gen = CodeGenPyServer(openapi, prod_package, test_package=test_package)
        packages = dict()
        code_gen._gen_handlers(packages)
        code_gen._gen_controllers(packages)
        code_gen._gen_models(packages)
        if test_package:
            code_gen._gen_handlers_tests(packages)
            code_gen._gen_controllers_tests(packages)
            code_gen._gen_models_tests(packages)
        return packages

    def _gen_handlers(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module().append("from ._mappings import MAPPINGS")
        modules["_handlers"] = self._gen_handlers_code()
        modules["_mappings"] = self._gen_mappings_code()
        packages[self._prod_package + ".handlers"] = modules

    def _gen_handlers_tests(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        modules["test_handlers"] = self._gen_handlers_tests_code()
        packages[self._test_package + ".handlers"] = modules

    def _gen_controllers(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                self._gen_controller_code(op, path_item.path, modules)
        packages[self._prod_package + ".controllers"] = modules

    def _gen_controllers_tests(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                self._gen_controller_test_code(op, path_item.path, modules)
        packages[self._test_package + ".controllers"] = modules

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

    def _gen_handlers_code(self) -> Code:
        code = self._gen_new_code_module()
        code.append("import tornado.escape")
        code.append()
        code.append("from ..webservice import WsRequestHandler")
        code.append("from ..reqparams import RequestParams")
        code.append(self._gen_controller_imports())
        code.append(self._gen_model_imports())

        for path_item in self._openapi.path_items:

            # Request class definition
            #
            class_name = self._get_py_handler_class_name(path_item.path)
            code.append()
            code.append()
            code.append("# noinspection PyAbstractClass,PyShadowingBuiltins")
            code.append(f"class {class_name}(WsRequestHandler):")
            with code.indent():
                for op in path_item.operations:

                    # HTTP method declaration
                    #
                    path_params = [p for p in op.parameters if p.in_ == "path"]
                    path_params_str_parts = []
                    for path_param in path_params:
                        path_params_str_parts.append(f"{path_param.name}: str")
                    path_params_str = ", ".join(path_params_str_parts)
                    code.append()
                    if path_params_str:
                        code.append(f"def {op.method}(self, {path_params_str}):")
                    else:
                        code.append(f"def {op.method}(self):")

                    with code.indent():
                        # HTTP method docs
                        #
                        if op.operation_id:
                            code.append(f'"""Provide API operation {op.operation_id}()."""')

                        req_mime_type, req_schema = self._select_handled_mime_type_and_schema_from_request_body(op)
                        req_py_type_name = self._get_py_type_name(req_schema) if req_schema else None

                        res_mime_type, res_schema = self._select_handled_mime_type_and_schema_from_response(op)
                        res_py_type_name = self._get_py_type_name(res_schema) if res_schema else None

                        # Get and convert parameters
                        #
                        req_params, opt_params = self._split_req_and_opt_parameters(op)
                        for param in req_params:
                            code.append(self._gen_fetch_param_code(param))
                        for param in opt_params:
                            code.append(self._gen_fetch_param_code(param))

                        # Get request body data
                        #
                        if req_py_type_name:
                            code.append(
                                f"# transform body with mime-type {req_mime_type} into a {req_py_type_name}")
                            if req_mime_type == "application/json":
                                if req_py_type_name == "Dict":
                                    code.append(f"data = tornado.escape.json_decode(self.request.body)")
                                else:
                                    code.append(f"data_dict = tornado.escape.json_decode(self.request.body)")
                                    code.append(f"data = {req_py_type_name}.from_dict(data_dict)")
                            elif req_mime_type == "text/plain":
                                code.append(f"data = self.request.body")
                            elif req_mime_type is not None:
                                code.append(f"# TODO (generated): transform self.request.body first")
                                code.append(f"data = self.request.body")
                            code.append()

                        # Call controller operation
                        #
                        func_name = self._get_py_op_func_name(op, class_name)
                        call_args_parts = []
                        for param in req_params:
                            py_name = self._get_py_lower_name(param.name, esc_builtins=True)
                            call_args_parts.append(f"{py_name}={py_name}")
                        if req_py_type_name is not None:
                            call_args_parts.append(f"data=data")
                        for param in opt_params:
                            py_name = self._get_py_lower_name(param.name, esc_builtins=True)
                            call_args_parts.append(f"{py_name}={py_name}")
                        call_args = ", ".join(call_args_parts)
                        if call_args:
                            code.append(f"result = {func_name}(self.ws_context, {call_args})")
                        else:
                            code.append(f"result = {func_name}(self.ws_context)")

                        # Convert controller operation's return value
                        #
                        if res_py_type_name:
                            code.append()
                            code.append(f"# transform result of type {res_py_type_name}"
                                        f" into response with mime-type {res_mime_type}")
                            if res_mime_type == "application/json":
                                code.append(f"self.set_header('Content-Type', '{res_mime_type}')")
                                if res_py_type_name in {"bool", "str", "int", "float", "List", "Dict"}:
                                    code.append(f"self.finish(tornado.escape.json_encode(result))")
                                else:
                                    code.append(f"self.finish(tornado.escape.json_encode(result.to_dict()))")
                            elif res_mime_type == "text/plain":
                                code.append(f"self.set_header('Content-Type', '{res_mime_type}')")
                                code.append(f"self.finish(result)")
                            elif res_mime_type is not None:
                                code.append(f"# TODO (generated): transform result first")
                                code.append(f"self.finish(result)")
                            else:
                                code.append(f"self.finish()")
                        else:
                            code.append(f"self.finish()")

        return code

    def _gen_handlers_tests_code(self) -> Code:
        code = self._gen_new_code_module()
        code.append("import unittest")
        code.append("import urllib.parse")
        code.append()
        code.append("import tornado.escape")
        code.append("import tornado.testing")
        code.append()

        code.append(f"from {self._prod_package}.app import new_application")
        code.append(f"from ..helpers import new_test_service_context")

        code.append()
        code.append()
        code.append("class WsTestCase(tornado.testing.AsyncHTTPTestCase):")
        with code.indent():
            code.append("def get_app(self):")
            with code.indent():
                code.append('"""Implements AsyncHTTPTestCase.get_app()."""')
                code.append("application = new_application()")
                code.append("application.ws_context = new_test_service_context()")
                code.append("return application")
            code.append()
            code.append("@property")
            code.append("def ctx(self):")
            with code.indent():
                code.append("return self._app.ws_context")

        for path_item in self._openapi.path_items:

            # Request class definition
            #
            class_name = self._get_py_handler_class_name(path_item.path)
            code.append()
            code.append()
            code.append(f"class {class_name}Test(WsTestCase):")
            with code.indent():

                for op in path_item.operations:

                    # HTTP method declaration
                    #
                    code.append()
                    code.append("@unittest.skip('not implemented yet')")
                    code.append(f"def test_{op.method}(self):")

                    with code.indent():
                        path_params = [p for p in op.parameters if p.in_ == "path"]
                        if path_params:
                            code.append()
                            code.append("# TODO (generated): set path parameter(s) to reasonable value(s)")
                            for param in path_params:
                                code.append(f"{param.name} = None")

                        query_params = [p for p in op.parameters if p.in_ == "query"]
                        if query_params:
                            code.append()
                            code.append("# TODO (generated): set query parameter(s) to reasonable value(s)")
                            for param in query_params:
                                code.append(f"{param.name} = None")

                        req_mime_type, req_schema = self._select_handled_mime_type_and_schema_from_request_body(op)
                        if req_schema:
                            code.append()
                            code.append("# TODO (generated): set data for request body to reasonable value")
                            if req_schema.type == "array" and req_mime_type == "application/json":
                                code.append("data = []")
                                code.append("body = tornado.escape.json_encode(data)")
                            elif req_schema.type == "object" and req_mime_type == "application/json":
                                code.append("data = {}")
                                code.append("body = tornado.escape.json_encode(data)")
                            else:
                                code.append("data = None")
                                code.append("body = data")

                        method_part = f', method={repr(op.method.upper())}'
                        body_part = ', body=body' if req_schema else ''
                        if query_params:
                            dict_items = ", ".join([f"{p.name}={p.name}" for p in query_params])
                            code.append(f"query = urllib.parse.urlencode(dict({dict_items}))")
                            query_part = "?{query}"
                            url_part = f'f\"{path_item.path}{query_part}\"'
                        else:
                            url_part = f'f\"{path_item.path}\"'

                        code.append()
                        code.append(f"response = self.fetch({url_part}{method_part}{body_part})")
                        code.append("self.assertEqual(200, response.code)")
                        code.append("self.assertEqual('OK', response.reason)")

                        res_mime_type, res_schema = self._select_handled_mime_type_and_schema_from_response(op)
                        code.append()
                        code.append("# TODO (generated): set expected_response correctly")
                        if res_schema:
                            if res_schema.type == "array" and res_mime_type == "application/json":
                                code.append("expected_response_data = []")
                                code.append("actual_response_data = []")
                                code.append(f"actual_response_data = tornado.escape.json_decode(response.body)")
                            elif res_schema.type == "object" and res_mime_type == "application/json":
                                code.append("expected_response_data = {}")
                                code.append(f"actual_response_data = tornado.escape.json_decode(response.body)")
                            else:
                                code.append(f"expected_response_data = None")
                                code.append(f"actual_response_data = response.body")
                        else:
                            code.append(f"expected_response_data = None")
                            code.append(f"actual_response_data = response.body")

                        code.append("self.assertEqual(expected_response_data, actual_response_data)")

        return code

    def _gen_controller_code(self, op: Operation, path: str, module_code: Dict[str, Code]):

        module_name = self._get_py_op_module_name(op)
        class_name = self._get_py_handler_class_name(path)
        func_name = self._get_py_op_func_name(op, class_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = self._gen_new_code_module()
            module_code[module_name] = code
            code.append("from typing import Dict, List")
            code.append()
            code.append("from ..context import WsContext")
            code.append(self._gen_model_imports())
            code.append(self._gen_assert_imports())

        req_params, opt_params = self._split_req_and_opt_parameters(op)

        req_mime_type, req_schema = self._select_handled_mime_type_and_schema_from_request_body(op)
        req_py_type_name = self._get_py_type_name(req_schema) if req_schema else None

        res_mime_type, res_schema = self._select_handled_mime_type_and_schema_from_response(op)
        res_py_type_name = self._get_py_type_name(res_schema) if res_schema else None

        py_return_type_code = f" -> {res_py_type_name}" if res_py_type_name else ""

        code.append()
        code.append()
        code.append("# noinspection PyUnusedLocal")
        params_decls = []
        for p in req_params:
            py_name = self._get_py_lower_name(p.name, esc_builtins=True)
            py_type = self._get_py_type_name(p.schema)
            params_decls.append((py_name, py_type, UNDEFINED))
        if req_py_type_name:
            params_decls.append(("data", req_py_type_name, UNDEFINED))
        for p in opt_params:
            py_name = self._get_py_lower_name(p.name, esc_builtins=True)
            py_type = self._get_py_type_name(p.schema)
            py_default = p.schema.default if p.schema.default is not UNDEFINED else None
            params_decls.append((py_name, py_type, py_default))

        if params_decls:
            code.append(f"def {func_name}(ctx: WsContext,")
            prefix = " " * (len(func_name) + 5)
            for i in range(len(params_decls)):
                py_name, py_type, py_default = params_decls[i]
                postfix = "," if i < len(params_decls) - 1 else f"){py_return_type_code}:"
                if py_default is UNDEFINED:
                    code.append(f"{prefix}{py_name}: {py_type}{postfix}")
                else:
                    code.append(f"{prefix}{py_name}: {py_type} = {repr(py_default)}{postfix}")

            with code.indent():
                for p in op.parameters:
                    code.append(self._gen_param_validation_code(p))
        else:
            code.append(f"def {func_name}(ctx: WsContext){py_return_type_code}:")

        with code.indent():
            code.append(f"# TODO (generated): implement operation {func_name}()")
            code.append(f"raise NotImplementedError('operation {func_name}() not yet implemented')")

    def _gen_controller_test_code(self, op: Operation, path: str, module_code: Dict[str, Code]):

        module_name = "test_" + self._get_py_op_module_name(op)
        test_class_name = self._get_py_op_test_class_name(op)
        handler_class_name = self._get_py_handler_class_name(path)
        func_name = self._get_py_op_func_name(op, handler_class_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = self._gen_new_code_module()
            module_code[module_name] = code
            code.append("import unittest")
            code.append()
            code.append(self._gen_controller_imports(package=self._prod_package + ".controllers"))
            code.append(self._gen_model_imports(package=self._prod_package + ".models"))
            code.append(f"from ..helpers import new_test_service_context")
            code.append()
            code.append()
            code.append(f"class {test_class_name}(unittest.TestCase):")
            code.append()
            with code.indent():
                code.append("def setUp(self):")
                with code.indent():
                    code.append("self.ctx = new_test_service_context()")

        with code.indent():
            code.append()
            code.append("@unittest.skip('not implemented yet')")
            code.append(f"def test_{func_name}(self):")
            with code.indent():
                req_params, opt_params = self._split_req_and_opt_parameters(op)

                if req_params:
                    code.append("# TODO (generated): set required parameters")
                    for param in req_params:
                        py_name = self._get_py_lower_name(param.name, esc_builtins=True)
                        code.append(f"{py_name} = None")

                req_mime_type, req_schema = self._select_handled_mime_type_and_schema_from_request_body(op)
                if req_schema:
                    if req_schema.type == "array":
                        code.append("# TODO (generated): set request data list items")
                        code.append(f"data = []")
                    elif req_schema.type == "object":
                        if req_schema.ref_name:
                            code.append(f"data = {req_schema.ref_name}()")
                            code.append("# TODO (generated): set request data properties")
                        else:
                            code.append("# TODO (generated): set request data dict items")
                            code.append("data = {}")
                    else:
                        code.append("# TODO (generated): set data")
                        code.append("data = None")

                if opt_params:
                    code.append("# TODO (generated): set optional parameters")
                    for param in opt_params:
                        py_name = self._get_py_lower_name(param.name, esc_builtins=True)
                        code.append(f"{py_name} = None")

                call_param_parts = []
                for param in req_params:
                    py_name = self._get_py_lower_name(param.name, esc_builtins=True)
                    call_param_parts.append(f"{py_name}")

                if req_schema:
                    call_param_parts.append(f"data=data")

                for param in opt_params:
                    py_name = self._get_py_lower_name(param.name, esc_builtins=True)
                    call_param_parts.append(f"{py_name}={py_name}")

                call_params = ", ".join(call_param_parts)

                code.append()
                if call_params:
                    code.append(f"result = {func_name}(self.ctx, {call_params})")
                else:
                    code.append(f"result = {func_name}(self.ctx)")

                res_mime_type, res_schema = self._select_handled_mime_type_and_schema_from_response(op)
                if res_schema:
                    if res_schema.type == "array":
                        code.append("self.assertIsInstance(result, list)")
                        code.append("# TODO (generated): set expected result")
                        code.append("expected_result = []")
                        code.append("self.assertEqual(expected_result, result)")
                    elif res_schema.type == "object":
                        if res_schema.ref_name:
                            code.append(f"self.assertIsInstance(result, {res_schema.ref_name})")
                            code.append(f"expected_result = {res_schema.ref_name}()")
                            code.append("# TODO (generated): set expected result properties")
                            code.append("self.assertEqual(expected_result, result)")
                        else:
                            code.append(f"self.assertIsInstance(result, dict)")
                            code.append("# TODO (generated): set expected result")
                            code.append("expected_result = {}")
                            code.append("self.assertEqual(expected_result, result)")
                    else:
                        code.append("# TODO (generated): set expected result")
                        code.append("expected_result = None")
                        code.append("self.assertEqual(expected_result, result)")
                else:
                    code.append("self.assertIsNone(result)")
