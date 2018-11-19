import unittest
from datetime import datetime

from eocdb.core.db.errors import OperationalError
from eocdb.core.models.dataset_query import DatasetQuery
from eocdb.core.models.qc_info import QC_INFO_STATUS_ONGOING, QC_INFO_STATUS_PASSED
from eocdb.db.mongo_db_driver import MongoDbDriver
from tests import helpers


class TestMongoDbDriver(unittest.TestCase):

    def setUp(self):
        self._driver = MongoDbDriver()
        self._driver.init(mock=True)

    def tearDown(self):
        self._driver.clear()
        self._driver.close()

    def test_connect_twice_throws(self):
        try:
            self._driver.connect()
            self.fail("OperationalError expected")
        except OperationalError:
            pass

    def test_insert_one_and_get(self):
        dataset = helpers.new_test_dataset(1)
        dataset.metadata["affiliations"] = "UCSB"
        dataset.metadata["received"] = "20160829"
        dataset.metadata["investigators"] = "Norm_Nelson"

        dataset.records = [[109.8, -38.4, 998, 20, 36],
                           [109.9, -38.3, 998, 20, 35]]

        ds_id = self._driver.add_dataset(dataset)

        result = self._driver.get_dataset(ds_id)
        self.assertIsNotNone(result)
        self.assertEqual("UCSB", result.metadata["affiliations"])
        self.assertEqual("Norm_Nelson", result.metadata["investigators"])
        self.assertEqual(2, len(result.records))
        self.assertAlmostEqual(109.8, result.records[0][0], 8)
        self.assertAlmostEqual(-38.3, result.records[1][1], 8)

    def test_get_invalid_id(self):
        dataset = helpers.new_test_dataset(2)

        self._driver.add_dataset(dataset)

        result = self._driver.get_dataset("rippelschnatz")
        self.assertIsNone(result)

    # noinspection PyTypeChecker
    def test_get_null_id(self):
        result = self._driver.get_dataset(None)
        self.assertIsNone(result)

    def test_insert_two_and_get_empty_expression(self):
        dataset = helpers.new_test_dataset(1)
        dataset.metadata["source"] = "we_don_t_care"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(2)
        dataset.metadata["source"] = "we_want_this"
        self._driver.add_dataset(dataset)

        result = self._driver.find_datasets(DatasetQuery())
        self.assertEqual(2, result.total_count)

    def test_insert_two_and_get_by_metadata_field(self):
        dataset = helpers.new_test_dataset(3)
        dataset.metadata["source"] = "we_don_t_care"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(4)
        dataset.metadata["source"] = "we_want_this"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="source: we_want_this")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-4.txt", result.datasets[0].path)

    def test_insert_three_and_get_by_metadata_field_and(self):
        dataset = helpers.new_test_dataset(3)
        dataset.metadata["affiliations"] = "we_don_t_care"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(4)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_2"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(5)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="affiliations: we_want_this AND cruise: baltic_1")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-5.txt", result.datasets[0].path)

        query = DatasetQuery(expr="affiliations: we_want_this AND cruise: baltic_2")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-4.txt", result.datasets[0].path)

    def test_insert_three_and_get_by_metadata_field_or(self):
        dataset = helpers.new_test_dataset(6)
        dataset.metadata["affiliations"] = "we_don_t_care"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(7)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_2"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(8)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="affiliations: we_want_this OR cruise: baltic_1")

        result = self._driver.find_datasets(query)
        self.assertEqual(3, result.total_count)
        self.assertEqual("archive/dataset-6.txt", result.datasets[0].path)

        query = DatasetQuery(expr="affiliations: we_want_this OR cruise: baltic_2")

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("archive/dataset-7.txt", result.datasets[0].path)

    def test_insert_and_get_by_not_existing_metadata_field(self):
        dataset = helpers.new_test_dataset(9)
        dataset.metadata["calibration_files"] = "yes_they_are_here"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="the_absent_field: not_there")
        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_and_get_by_path(self):
        dataset = helpers.new_test_dataset(9)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(10)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="path:archive/dataset-10.txt")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-10.txt", result.datasets[0].path)


    def test_insert_and_get_by_path_single_char_wildcard(self):
        dataset = helpers.new_test_dataset(13)
        dataset.path = "/home/eocdb/store/BIGELOW/BALCH/gnats/archive/chl/chl-s170604w.sub"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(14)
        dataset.path = "/home/eocdb/store/BIGELOW/BALCH/gnats/archive/chl/chl-s170605w.sub"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(15)
        dataset.path = "/home/eocdb/store/BIGELOW/BALCH/gnats/archive/chl/chl-s170804w.sub"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="path:/home/eocdb/store/BIGELOW/BALCH/gnats/archive/chl/chl-s17060?w.sub")

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("/home/eocdb/store/BIGELOW/BALCH/gnats/archive/chl/chl-s170604w.sub",
                         result.datasets[0].path)
        self.assertEqual("/home/eocdb/store/BIGELOW/BALCH/gnats/archive/chl/chl-s170605w.sub",
                         result.datasets[1].path)

    def test_insert_and_get_by_path_multi_char_wildcard(self):
        dataset = helpers.new_test_dataset(13)
        dataset.path = "archive/Helga.txt"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(14)
        dataset.path = "archive/Helma.txt"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(15)
        dataset.path = "archive/Olga.txt"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="path:*ga")

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("archive/Helga.txt", result.datasets[0].path)
        self.assertEqual("archive/Olga.txt", result.datasets[1].path)

    def test_insert_and_get_by_qc_status(self):
        dataset = helpers.new_test_dataset(13)
        dataset.metadata["qc_status"] = QC_INFO_STATUS_ONGOING
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(14)
        dataset.metadata["qc_status"] = QC_INFO_STATUS_PASSED
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="qc_status:" + QC_INFO_STATUS_PASSED)

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-14.txt", result.datasets[0].path)

    def test_get_offset_only(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(offset=1)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("archive/dataset-0.txt", result.datasets[0].path)

        query = DatasetQuery(offset=2)
        result = self._driver.find_datasets(query)
        self.assertEqual(9, result.total_count)
        self.assertEqual("archive/dataset-1.txt", result.datasets[0].path)

        query = DatasetQuery(offset=6)
        result = self._driver.find_datasets(query)
        self.assertEqual(5, result.total_count)
        self.assertEqual("archive/dataset-5.txt", result.datasets[0].path)

    def test_get_count_only(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(count=4)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("archive/dataset-0.txt", result.datasets[0].path)

        query = DatasetQuery(count=7)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("archive/dataset-0.txt", result.datasets[0].path)

    def test_get_count_zero_returns_number_of_results(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(count=0)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual([], result.datasets)

    def test_get_offset_and_count(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(offset=2, count=4)
        result = self._driver.find_datasets(query)
        self.assertEqual(9, result.total_count)
        self.assertEqual("archive/dataset-1.txt", result.datasets[0].path)

        query = DatasetQuery(offset=5, count=3)
        result = self._driver.find_datasets(query)
        self.assertEqual(6, result.total_count)
        self.assertEqual("archive/dataset-4.txt", result.datasets[0].path)

        query = DatasetQuery(offset=8, count=5)
        result = self._driver.find_datasets(query)
        self.assertEqual(3, result.total_count)
        self.assertEqual("archive/dataset-7.txt", result.datasets[0].path)

    def test_get_offset_and_negative_count(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(offset=1, count=-1)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("archive/dataset-0.txt", result.datasets[0].path)
        self.assertEqual("archive/dataset-9.txt", result.datasets[9].path)

        query = DatasetQuery(offset=4, count=-1)
        result = self._driver.find_datasets(query)
        self.assertEqual(7, result.total_count)
        self.assertEqual("archive/dataset-3.txt", result.datasets[0].path)

    def test_insert_two_and_get_by_location(self):
        dataset = helpers.new_test_db_dataset(11)
        dataset.add_geo_location(lon=-76.3461, lat=39.0652)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(12)
        dataset.add_geo_location(lon=-76.4373, lat=38.7354)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(region=[-77.0, 38.0, -76.0, 38.9])  # covers second dataset tb 2018-10-23

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-12.txt", result.datasets[0].path)

    def test_insert_two_and_get_by_location_many_records(self):
        dataset = helpers.new_test_db_dataset(13)
        dataset.add_geo_location(lon=-69.8150, lat=42.7250)
        dataset.add_geo_location(lon=-69.8167, lat=42.7158)
        dataset.add_geo_location(lon=-69.7675, lat=43.1685)
        dataset.add_geo_location(lon=-70.2030, lat=43.1400)
        dataset.add_geo_location(lon=-70.2053, lat=42.5045)
        dataset.add_geo_location(lon=-69.5458, lat=42.7790)
        dataset.add_geo_location(lon=-69.1059, lat=42.5036)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(14)
        dataset.add_geo_location(lon=-158.750, lat=20.421)
        dataset.add_geo_location(lon=-160.182, lat=18.892)
        dataset.add_geo_location(lon=-161.317, lat=17.672)
        dataset.add_geo_location(lon=-163.296, lat=15.519)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(region=[-71.0, 43.0, -70.0, 43.5])  # covers first dataset tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-13.txt", result.datasets[0].path)

    def test_insert_two_and_get_by_location_and_metadata(self):
        dataset = helpers.new_test_db_dataset(15)
        dataset.metadata["data_status"] = "final"
        dataset.add_geo_location(lon=82, lat=-10)
        dataset.add_geo_location(lon=82.5, lat=-10.3)
        dataset.add_geo_location(lon=82.8, lat=-10.19)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(16)
        dataset.metadata["data_status"] = "test"
        dataset.add_geo_location(lon=16.8, lat=-72.34)
        dataset.add_geo_location(lon=16.7, lat=-71.98)
        dataset.add_geo_location(lon=16.69, lat=-72.11)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr='data_status: test', region=[15.0, -75.0, 17.0, -70.0])  # covers second dataset tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-16.txt", result.datasets[0].path)

        query = DatasetQuery(expr='data_status: test', region=[25.0, -75.0, 27.0, -70.0])  # region does not match tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

        query = DatasetQuery(expr='data_status: experimental', region=[15.0, -75.0, 17.0, -70.0])  # status does not match tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_two_and_get_by_time_interval(self):
        dataset = helpers.new_test_db_dataset(17)
        dataset.metadata["data_type"] = "bottle"
        dataset.add_time(datetime(2008, 7, 11, 14, 16, 22))
        dataset.add_time(datetime(2008, 7, 11, 14, 17, 19))
        dataset.add_time(datetime(2008, 7, 11, 14, 18, 4))
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(18)
        dataset.metadata["data_type"] = "cup"
        dataset.add_time(datetime(2008, 8, 23, 16, 41, 9))
        dataset.add_time(datetime(2008, 8, 23, 16, 41, 54))
        dataset.add_time(datetime(2008, 8, 23, 16, 42, 46))
        self._driver.add_dataset(dataset)

        query = DatasetQuery(time=["2008-07-11T00:00:00", "2008-07-11T23:59:59"])  # covers first dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-17.txt", result.datasets[0].path)

        query = DatasetQuery(time=["2008-08-23T00:00:00", "2008-08-23T23:59:59"])  # covers second dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-18.txt", result.datasets[0].path)

        query = DatasetQuery(time=["2007-01-01T00:00:00", "2008-08-23T23:59:59"])  # covers both datasets tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("archive/dataset-17.txt", result.datasets[0].path)
        self.assertEqual("archive/dataset-18.txt", result.datasets[1].path)

        query = DatasetQuery(time=["2005-01-01T00:00:00", "2005-01-01T23:59:59"])  # covers no dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_two_and_get_by_time_interval_no_start_date(self):
        dataset = helpers.new_test_db_dataset(17)
        dataset.metadata["data_type"] = "bottle"
        dataset.add_time(datetime(2008, 7, 11, 14, 16, 22))
        dataset.add_time(datetime(2008, 7, 11, 14, 17, 19))
        dataset.add_time(datetime(2008, 7, 11, 14, 18, 4))
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(18)
        dataset.metadata["data_type"] = "cup"
        dataset.add_time(datetime(2008, 8, 23, 16, 41, 9))
        dataset.add_time(datetime(2008, 8, 23, 16, 41, 54))
        dataset.add_time(datetime(2008, 8, 23, 16, 42, 46))
        self._driver.add_dataset(dataset)

        query = DatasetQuery(time=[None, "2008-07-11T23:59:59"])  # covers first dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-17.txt", result.datasets[0].path)

        query = DatasetQuery(time=[None, "2010-01-01T23:59:59"])  # covers both datasets tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("archive/dataset-17.txt", result.datasets[0].path)
        self.assertEqual("archive/dataset-18.txt", result.datasets[1].path)

        query = DatasetQuery(time=[None, "2001-01-01T23:59:59"])  # covers no dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_two_and_get_by_time_interval_no_end_date(self):
        dataset = helpers.new_test_db_dataset(17)
        dataset.metadata["data_type"] = "bottle"
        dataset.add_time(datetime(2008, 7, 11, 14, 16, 22))
        dataset.add_time(datetime(2008, 7, 11, 14, 17, 19))
        dataset.add_time(datetime(2008, 7, 11, 14, 18, 4))
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(18)
        dataset.metadata["data_type"] = "cup"
        dataset.add_time(datetime(2008, 8, 23, 16, 41, 9))
        dataset.add_time(datetime(2008, 8, 23, 16, 41, 54))
        dataset.add_time(datetime(2008, 8, 23, 16, 42, 46))
        self._driver.add_dataset(dataset)

        query = DatasetQuery(time=["2008-08-20T00:00:00", None])  # covers second dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-18.txt", result.datasets[0].path)

        query = DatasetQuery(time=["2007-01-01T00:00:00", None])  # covers both datasets tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("archive/dataset-17.txt", result.datasets[0].path)
        self.assertEqual("archive/dataset-18.txt", result.datasets[1].path)

        query = DatasetQuery(time=["2010-01-01T23:59:59", None])  # covers no dataset tb 2018-10-29

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_two_and_get_by_attributes_non_matching(self):
        dataset = helpers.new_test_db_dataset(18)
        dataset.attributes = ["a", "b"]
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(19)
        dataset.attributes = ["Chl_a", "b"]
        self._driver.add_dataset(dataset)

        query = DatasetQuery(pgroup=["sal"])
        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_two_and_get_by_attributes_one_matching(self):
        dataset = helpers.new_test_db_dataset(20)
        dataset.attributes = ["a", "b"]
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(21)
        dataset.attributes = ["Chl_a", "b"]
        self._driver.add_dataset(dataset)

        query = DatasetQuery(pgroup=["Chl_a"])
        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("archive/dataset-21.txt", result.datasets[0].path)

    def test_insert_two_and_get_by_attributes_both_matching(self):
        dataset = helpers.new_test_db_dataset(22)
        dataset.attributes = ["a", "b"]
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(23)
        dataset.attributes = ["Chl_a", "b"]
        self._driver.add_dataset(dataset)

        query = DatasetQuery(pgroup=["b"])
        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("archive/dataset-22.txt", result.datasets[0].path)
        self.assertEqual("archive/dataset-23.txt", result.datasets[1].path)

    def test_insert_two_and_get_by_attributes_two_groups_both_matching(self):
        dataset = helpers.new_test_db_dataset(24)
        dataset.attributes = ["a", "b"]
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(25)
        dataset.attributes = ["Chl_a", "b"]
        self._driver.add_dataset(dataset)

        query = DatasetQuery(pgroup=["a", "Chl_a"])
        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)

    def test_get_get_start_index_and_page_size(self):
        query = DatasetQuery()
        query.offset = 1
        self.assertEqual((0, 1000), self._driver._get_start_index_and_count(query))

        query.offset = 12
        query.count = 106
        self.assertEqual((11, 106), self._driver._get_start_index_and_count(query))

        query.offset = 14
        query.count = None
        self.assertEqual((13, 0), self._driver._get_start_index_and_count(query))

    def test_get_get_start_index_and_page_size_raises_on_offset_zero(self):
        query = DatasetQuery()
        query.offset = 0

        try:
            self._driver._get_start_index_and_count(query)
            self.fail("ValueError expected")
        except ValueError:
            pass

    def test_get_get_start_index_and_negative_page_size(self):
        query = DatasetQuery()
        query.offset = 1
        query.count = -1
        self.assertEqual((0, 0), self._driver._get_start_index_and_count(query))

    def test_to_dataset_ref(self):
        dataset_dict = {"_id": "nasenmann.org", "path": "/where/is/your/mama/gone/Rosamunde"}

        dataset_ref = self._driver._to_dataset_ref(dataset_dict)
        self.assertEqual("nasenmann.org", dataset_ref.id)
        self.assertEqual("/where/is/your/mama/gone/Rosamunde", dataset_ref.path)

    def test_convert_times_empty(self):
        dict = {'path': 'archive/dataset-17.txt',
                'times': []}

        converted_dict = self._driver._convert_times(dict)
        self.assertEqual([], converted_dict["times"])

    def test_convert_times_two_values(self):
        dict = {'path': 'archive/dataset-17.txt',
                'times': ['2008-07-11T14:16:22', '2008-07-11T14:17:08']}

        converted_dict = self._driver._convert_times(dict)
        self.assertEqual([datetime(2008, 7, 11, 14, 16, 22), datetime(2008, 7, 11, 14, 17, 8)], converted_dict["times"])

    def _add_test_datasets_to_db(self):
        for i in range(0, 10):
            dataset = helpers.new_test_dataset(i)
            self._driver.add_dataset(dataset)