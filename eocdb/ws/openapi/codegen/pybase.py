import builtins
from typing import List, Dict, Tuple

from .code import Code
from .constants import LICENSE_AND_COPYRIGHT
from ..model import OpenAPI, Operation, Schema, Parameter, Property
from ....core import UNDEFINED

_PY_LICENSE_AND_COPYRIGHT = '\n'.join(['# ' + l for l in LICENSE_AND_COPYRIGHT.split('\n')])

_TYPE_TO_PY_TYPE_MAP = dict(string="str", number="float", boolean="bool", integer="int", array='List', object="Dict")


class CodeGenPy:
    def __init__(self, openapi: OpenAPI):
        self._openapi = openapi

    def _gen_controller_imports(self, package: str = "..controllers") -> Code:
        module_names = set()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                module_name = self._get_py_op_module_name(op)
                module_names.add(module_name)
        code = Code()
        for module_name in sorted(module_names):
            code.append(f"from {package}.{module_name} import *")
        return code

    def _gen_model_imports(self, package: str = "..models", excluded_schema_name: str = None) -> Code:
        schema_names = set(schema_name for schema_name in self._openapi.components.schemas
                           if not excluded_schema_name or excluded_schema_name != schema_name)
        code = Code()
        for schema_name in sorted(schema_names):
            code.append(f"from {package}.{self._get_py_lower_name(schema_name)} import {schema_name}")
        return code

    @classmethod
    def _gen_fetch_param_code(cls, param) -> Code:
        py_name = cls._get_py_lower_name(param.name, esc_builtins=True)
        py_type = cls._get_py_type_name(param.schema)
        if py_type == "str":
            type_suffix = ""
        elif py_type == "List[str]":
            type_suffix = "_list"
        elif py_type == "List[bool]":
            type_suffix = "_bool_list"
        elif py_type == "List[int]":
            type_suffix = "_int_list"
        elif py_type == "List[float]":
            type_suffix = "_float_list"
        else:
            type_suffix = "_" + py_type
        source = param.in_
        if source == "path":
            if py_type == "str":
                if py_name != param.name:
                    return Code(f"{py_name} = {param.name}")
                else:
                    return Code()
            else:
                return Code(f"{py_name} = RequestParams.to{type_suffix}('{param.name}', {param.name})")
        else:
            return Code(f"{py_name} = self.{source}.get_param{type_suffix}('{param.name}', "
                        f"default={repr(param.schema.default)})")

    def _gen_model_code(self, schema_name: str, schema: Schema, module_code: Dict[str, Code]):
        module_name = self._get_py_lower_name(schema_name, esc_builtins=True)
        class_name = self._get_py_camel_name(schema_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = self._gen_new_code_module()
            module_code[module_name] = code
            code.append("from typing import Dict, List, Optional")
            code.append()
            code.append("from ..model import Model")
            code.append(self._gen_model_imports(package="", excluded_schema_name=schema_name))
            code.append(self._gen_assert_imports())

        if schema.properties:
            for p in schema.properties:
                if p.schema.enum:
                    code.append()
                    name_prefix = self._get_py_upper_name(schema_name) + "_" + self._get_py_upper_name(p.name)
                    for e in p.schema.enum:
                        e_name = str(e).replace(' ', '_').replace('-', '_').upper()
                        code.append(f"{name_prefix}_{e_name} = {repr(e)}")

        code.append()
        code.append()
        code.append(f"class {class_name}(Model):")
        with code.indent():
            code.append('"""')
            if schema.description:
                code.append(schema.description)
            else:
                code.append(f'The {class_name} model.')
            code.append('"""')

            code.append()
            if schema.properties:
                req_props, _opt_props = self._split_req_and_opt_properties(schema)
                param_decls = []
                for p in req_props:
                    py_name = self._get_py_lower_name(p.name, esc_builtins=True)
                    py_type = self._get_py_type_name(p.schema)
                    param_decls.append((py_name, py_type, UNDEFINED))
                for p in _opt_props:
                    py_name = self._get_py_lower_name(p.name, esc_builtins=True)
                    py_type = self._get_py_type_name(p.schema)
                    py_default = p.schema.default if p.schema.default is not UNDEFINED else None
                    param_decls.append((py_name, py_type, py_default))
                code.append(f"def __init__(self,")
                prefix = 13 * " "
                for i in range(len(param_decls)):
                    py_name, py_type, py_default = param_decls[i]
                    postfix = "," if i < len(param_decls) - 1 else "):"
                    if py_default is UNDEFINED:
                        code.append(f"{prefix}{py_name}: {py_type}{postfix}")
                    else:
                        code.append(f"{prefix}{py_name}: {py_type} = {repr(py_default)}{postfix}")

            with code.indent():
                if schema.properties:
                    for p in schema.properties:
                        code.append(self._gen_param_validation_code(self._prop_to_param(p, schema)))
                    for p in schema.properties:
                        py_param_name = self._get_py_lower_name(p.name, esc_builtins=True)
                        py_prop_name = self._get_py_lower_name(p.name, esc_builtins=False)
                        code.append(f"self._{py_prop_name} = {py_param_name}")
                else:
                    code.append(f"pass")

            if schema.properties:
                for p in schema.properties:
                    py_name = self._get_py_lower_name(p.name, esc_builtins=False)
                    py_type = self._get_py_type_name(p.schema)
                    required = schema.required and p.name in schema.required
                    if not required:
                        py_type = f"Optional[{py_type}]"
                    code.append()
                    code.append(f"@property")
                    code.append(f"def {py_name}(self) -> {py_type}:")
                    with code.indent():
                        code.append(f"return self._{py_name}")

                    code.append()
                    code.append(f"@{py_name}.setter")
                    code.append(f"def {py_name}(self, value: {py_type}):")
                    with code.indent():
                        code.append(self._gen_param_validation_code(self._prop_to_param(p, schema, name="value")))
                        code.append(f"self._{py_name} = value")

    def _gen_model_tests_code(self, schema_name: str, schema: Schema, modules: Dict[str, Code]):
        # Should generate test code here, but models are actually just stupid object structures
        pass

    @classmethod
    def _prop_to_param(cls, prop: Property, schema: Schema, name: str = None) -> Parameter:
        return Parameter(name=name if name else prop.name,
                         schema=prop.schema,
                         in_="query",
                         required=schema.required and prop.name in schema.required)

    def _gen_mappings_code(self) -> Code:
        code = self._gen_new_code_module()
        code.append("from ._handlers import *")
        code.append("from ..webservice import url_pattern")
        code.append()
        code.append("MAPPINGS = [")
        with code.indent():
            for path_item in self._openapi.path_items:
                class_name = self._get_py_handler_class_name(path_item.path)
                code.append(f"(url_pattern('{path_item.path}'), {class_name}),")
        code.append("]")
        return code

    @classmethod
    def _gen_param_validation_code(cls, param: Parameter) -> Code:
        code = Code()
        nullable = not param.required or param.schema.nullable
        py_param_name = cls._get_py_lower_name(param.name, esc_builtins=True)
        if not nullable and not param.allow_empty_value:
            code.append(f"assert_not_none_not_empty({py_param_name}, name='{py_param_name}')")
        elif not nullable:
            code.append(f"assert_not_none({py_param_name}, name='{py_param_name}')")
        elif not param.allow_empty_value:
            code.append(f"assert_not_empty({py_param_name}, name='{py_param_name}')")
        if param.schema.enum:
            code.append(f"assert_one_of({py_param_name}, {repr(param.schema.enum)}, name='{py_param_name}')")
        return code

    @classmethod
    def _gen_new_code_module(cls) -> Code:
        code = Code(_PY_LICENSE_AND_COPYRIGHT)
        code.append()
        code.append()
        return code

    @classmethod
    def _gen_assert_imports(cls) -> Code:
        return Code("from ...core.asserts import"
                    " assert_not_empty,"
                    " assert_not_none,"
                    " assert_not_none_not_empty,"
                    " assert_one_of")

    @classmethod
    def _get_py_op_module_name(cls, op: Operation):
        return op.tags[0].lower() if op.tags and len(op.tags) else "default"

    @classmethod
    def _get_py_op_test_class_name(cls, op: Operation):
        return cls._get_py_camel_name(op.tags[0]) + "Test" if op.tags and len(op.tags) else "Test"

    @classmethod
    def _get_py_type_name(cls, schema: Schema) -> str:
        if schema.ref_name:
            return schema.ref_name

        if schema.type == 'array':
            item_schema = schema.items
            if item_schema:
                py_item_type = cls._get_py_type_name(item_schema)
                return f"List[{py_item_type}]"

        return _TYPE_TO_PY_TYPE_MAP[schema.type]

    @classmethod
    def _select_handled_mime_type_and_schema_from_request_body(cls, op: Operation):
        req_mime_type = req_schema = None
        if op.request_body and op.request_body.content:
            req_mime_type, req_schema = cls._select_handled_mime_type_and_schema(op.request_body.content)
        return req_mime_type, req_schema

    @classmethod
    def _select_handled_mime_type_and_schema_from_response(cls, op: Operation):
        res_mime_type = res_schema = None
        if op.responses:
            response = op.responses.get("200") or op.responses.get("default")
            if response and response.content:
                res_mime_type, res_schema = cls._select_handled_mime_type_and_schema(response.content)
        return res_mime_type, res_schema

    @classmethod
    def _select_handled_mime_type_and_schema(cls, content: Dict[str, Schema]) -> Tuple[str, Schema]:
        if not content:
            raise ValueError("empty content")
        json_schema = content.get("application/json")
        if json_schema:
            return "application/json", json_schema
        json_schema = content.get("text/json")
        if json_schema:
            return "application/json", json_schema
        json_schema = content.get("text/plain")
        if json_schema:
            return "text/plain", json_schema
        json_schema = content.get("multipart/form-data")
        if json_schema:
            return "multipart/form-data", json_schema
        json_schema = content.get("application/octet-stream")
        if json_schema:
            return "application/octet-stream", json_schema
        raise ValueError(f'content with only unsupported mime-type(s): {set(content.keys())}')

    @classmethod
    def _get_py_lower_name(cls, name: str, esc_builtins: bool = False):
        """Gen name for Python packages, modules, functions, methods, properties, variables."""
        py_name = ''
        n = len(name)
        for i in range(n):
            c = name[i]
            if c.islower() and i < n - 1 and name[i + 1].isupper():
                py_name += c
                py_name += "_"
            else:
                py_name += c.lower()
        if esc_builtins and hasattr(builtins, py_name):
            py_name += '_'
        return py_name

    @classmethod
    def _get_py_upper_name(cls, name: str):
        """Gen name for Python constants."""
        return cls._get_py_lower_name(name).upper()

    @classmethod
    def _get_py_camel_name(cls, s: str):
        """Gen name for Python classes."""
        n = len(s)
        if n == 0:
            return s
        s2 = s[0].upper()
        for i in range(1, n):
            c = s[i]
            if s[i - 1] == "_":
                s2 += c.upper()
            elif c != '_':
                s2 += c
        return s2

    @classmethod
    def _get_py_handler_class_name(cls, path: str) -> str:
        if path.startswith('/'):
            path = path[1:]
        return cls._get_py_camel_name(path.replace('/', '_').replace('{', '').replace('}', '').lower())

    @classmethod
    def _get_py_op_func_name(cls, op: Operation, class_name: str):
        return cls._get_py_lower_name(op.operation_id if op.operation_id else op.method + class_name, esc_builtins=True)

    @classmethod
    def _split_req_and_opt_parameters(cls, op: Operation) -> Tuple[List[Parameter], List[Parameter]]:
        required_params = []
        optional_params = []
        if op.parameters:
            for p in op.parameters:
                if p.required or p.in_ == "path" or p.schema.default is UNDEFINED:
                    required_params.append(p)
                else:
                    optional_params.append(p)
        return required_params, optional_params

    @classmethod
    def _split_req_and_opt_properties(cls, schema: Schema) -> Tuple[List[Property], List[Property]]:
        required_props = []
        optional_props = []
        if schema.properties:
            for p in schema.properties:
                if schema.required and p.name in schema.required:
                    required_props.append(p)
                else:
                    optional_props.append(p)
        return required_props, optional_props
