import unittest

from eocdb.core import QueryParser
from eocdb.db.mongo_query_generator import MongoQueryGenerator


class TestMongoQueryGenerator(unittest.TestCase):

    def setUp(self):
        self.mongo_gen = MongoQueryGenerator()

    def test_empty_query(self):
        self.assertEqual(None, self.mongo_gen.query)

    def test_query_field_value_equal_string(self):
        q = QueryParser.parse('investigators:Robert_Vaillancourt')
        q.accept(self.mongo_gen)

        self.assertEqual({'investigators' : 'Robert_Vaillancourt'}, self.mongo_gen.query)

    def test_query_field_value_equal_float(self):
        q = QueryParser.parse('north_latitude:42.4853')
        q.accept(self.mongo_gen)

        self.assertEqual({'north_latitude' : 42.4853}, self.mongo_gen.query)

    def test_query_field_values_AND(self):
        q = QueryParser.parse('cruise:KN219 AND data_type:bottle')
        q.accept(self.mongo_gen)

        self.assertEqual({'cruise' : 'KN219', 'data_type' : 'bottle'}, self.mongo_gen.query)

    def test_query_field_values_OR(self):
        q = QueryParser.parse('cruise:KN219 OR data_type:bottle')
        q.accept(self.mongo_gen)

        self.assertEqual({'$or': [{'cruise' : 'KN219'}, {'data_type' : 'bottle'}]}, self.mongo_gen.query)

    def test_query_field_value_range(self):
        q = QueryParser.parse('south_latitude:[-25.6 TO -22.5]')
        q.accept(self.mongo_gen)

        self.assertEqual({'south_latitude' : {'$gte' : -25.6, '$lte' : -22.5}}, self.mongo_gen.query)


    # less than
    # less than equal
    # greater
    # greater than equal
    # multi character wildcards
    # single character wildcard
    # dates (and relations)
