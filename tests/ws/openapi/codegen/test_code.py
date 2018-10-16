import unittest

from eocdb.ws.openapi.codegen import Code


class CodeTest(unittest.TestCase):
    def test_append_code_str(self):
        code = Code()
        code.append("line1")
        with code.indent():
            code.append("line2")
            with code.indent():
                code.append("line3")
                code.append("line4")
            code.append("line5")
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
        with inner_code.indent():
            inner_code.append("iline2")
            with inner_code.indent():
                inner_code.append("iline3")
                inner_code.append("iline4")
            inner_code.append("iline5")
        inner_code.append("iline6")

        outer_code = Code()
        outer_code.append(["# outer"])
        with outer_code.indent():
            outer_code.append(["# inner"])
            outer_code.append(inner_code)

        self.assertEqual(['# outer',
                          '    # inner',
                          '    iline1',
                          '        iline2',
                          '            iline3',
                          '            iline4',
                          '        iline5',
                          '    iline6'],
                         outer_code.lines)
