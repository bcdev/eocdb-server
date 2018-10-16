import os
from contextlib import contextmanager
from typing import List, Dict, Union

_TAB = "    "

Modules = Dict[str, "Code"]
Packages = Dict[str, Modules]


class Code:
    """
    Generates Python code from a valid(!) OpenAPI 3.0.0 document.

    See also

    * https://swagger.io/docs/specification
    * https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md

    """

    def __init__(self, part: Union[str, list, "Code"] = None):
        self._indent = 0
        self._lines = []
        if part is not None:
            self.append(part)

    @contextmanager
    def indent(self):
        try:
            self.inc_indent()
            yield self._indent
        finally:
            self.dec_indent()

    def inc_indent(self):
        self._indent += 1

    def dec_indent(self):
        self._indent -= 1

    def append(self, part: Union[str, list, "Code"] = None) -> "Code":
        if isinstance(part, Code):
            self.append(part.lines)
        elif isinstance(part, list):
            for line in part:
                self.append(line)
        elif isinstance(part, str):
            tabs = self._indent * _TAB
            self._lines.append(tabs + part)
        elif part is None:
            self._lines.append("")
        else:
            raise TypeError(f'part of unsupported type {type(part)}')
        return self

    @property
    def lines(self) -> List[str]:
        return self._lines

    @classmethod
    def write_packages(cls, base_dir: str, packages: Packages):
        for package, modules in packages.items():
            cls.write_modules(base_dir, package, modules)

    @classmethod
    def write_modules(cls, base_dir: str, package: str, modules: Modules):
        package_dir = os.path.join(base_dir, *package.split("."))
        os.makedirs(package_dir, exist_ok=True)
        for module_name, module_code in modules.items():
            cls.write_module(package_dir, module_name, module_code)

    @classmethod
    def write_module(cls, package_dir: str, module_name: str, code: "Code"):
        with open(os.path.join(package_dir, module_name + ".py"), "w") as fp:
            fp.writelines(line + "\n" for line in code.lines)
