import os
import unittest

from eocdb.ws.openapi.codegen import CodeGen
from eocdb.ws.openapi.parser import Parser


class CodeGenTest(unittest.TestCase):
    def test_gen_code(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eocdb", "ws", "res", "openapi.yml")

        open_api = Parser.from_yaml(file)
        self.assertIsNotNone(open_api)

        packages = CodeGen.gen_py_server_code(open_api, "eocdb.ws")
        self.assertIsNotNone(packages)
        self.assertEqual(3, len(packages))

        packages = CodeGen.gen_py_server_code(open_api, "eocdb.ws", "tests.ws")
        self.assertIsNotNone(packages)
        self.assertEqual(6, len(packages))
