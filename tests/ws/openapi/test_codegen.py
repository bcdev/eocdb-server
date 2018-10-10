import os
import unittest

from eocdb.ws.openapi.codegen import Code, CodeGen
from eocdb.ws.openapi.parser import Parser


class CodeGenTest(unittest.TestCase):
    def test_gen_code(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "eocdb", "ws", "res", "openapi.yml")

        open_api = Parser.from_yaml(file)
        self.assertIsNotNone(open_api)

        code_gen = CodeGen(open_api)
        packages = code_gen.gen_code("ws.impl")

        self.assertIsNotNone(packages)
        self.assertEqual(3, len(packages))


class CodeTest(unittest.TestCase):
    def test_append_code_str(self):
        code = Code()
        code.append("line1")
        code.inc_indent()
        code.append("line2")
        code.inc_indent()
        code.append("line3")
        code.append("line4")
        code.dec_indent()
        code.append("line5")
        code.dec_indent()
        code.append("line6")

        self.assertEqual(['line1',
                          '    line2',
                          '        line3',
                          '        line4',
                          '    line5',
                          'line6'],
                         code.lines)

    def test_append_code_code(self):
        inner_code = Code()
        inner_code.append("iline1")
        inner_code.inc_indent()
        inner_code.append("iline2")
        inner_code.inc_indent()
        inner_code.append("iline3")
        inner_code.append("iline4")
        inner_code.dec_indent()
        inner_code.append("iline5")
        inner_code.dec_indent()
        inner_code.append("iline6")

        outer_code = Code()
        outer_code.append(["# outer"])
        outer_code.inc_indent()
        outer_code.append(["# inner"])
        outer_code.append(inner_code)
        outer_code.dec_indent()

        self.assertEqual(['# outer',
                          '    # inner',
                          '    iline1',
                          '        iline2',
                          '            iline3',
                          '            iline4',
                          '        iline5',
                          '    iline6'],
                         outer_code.lines)
