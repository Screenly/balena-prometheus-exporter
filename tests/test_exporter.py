import unittest
from unittest import mock
from main import BalenaCollector


class TestBalenaCollector(unittest.TestCase):
    def setUp(self):
        self.collector = BalenaCollector()

    @mock.patch("main.BalenaCollector.get_fleet_metrics")
    def test_collect(self, mock_metrics):
        with mock.patch.object(self.collector, "get_balena_fleets") as mock_fleets:
            mock_fleets.return_value = ["fleet1", "fleet2"]
            mock_metrics.side_effect = [("test_fleet", 3), ("test_fleet", 3)]

            result = list(self.collector.collect()[0].samples)
            expected = [('balena_devices_online', {'fleet_name': 'test_fleet'}, 3),
                        ('balena_devices_online', {'fleet_name': 'test_fleet'}, 3)]

            result = [(s.name, s.labels, s.value) for s in result]

            self.assertEqual(result, expected)

    def test_get_balena_fleets(self):
        with mock.patch("main.requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"d": [{"id": "fleet1"}, {"id": "fleet2"}]}
            result = list(self.collector.get_balena_fleets())
            expected = ["fleet1", "fleet2"]
            self.assertEqual(result, expected)


    def test_get_fleet_metrics(self):
        with mock.patch("main.requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"d": [{"owns__device": 3, "app_name": "test_fleet"}]}
            result = self.collector.get_fleet_metrics("fleet1")
            expected = ("test_fleet", 3)
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
