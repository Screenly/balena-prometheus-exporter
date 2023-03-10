import os
import sys
import time

import requests
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, CounterMetricFamily, GaugeMetricFamily

BALENA_TOKEN = os.getenv("BALENA_TOKEN", False)
CRAWL_INTERVAL = os.getenv("CRAWL_INTERVAL", 60)


class BalenaCollector(object):
    def __init__(self):
        pass

    def get_balena_fleets(self):
        """
        Get all the fleets that the user has access to
        and return all corresponding fleet IDs
        """

        fleets = []
        headers = {
            "Authorization": f"Bearer {BALENA_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            "https://api.balena-cloud.com/v6/application?$filter=is_directly_accessible_by__user/any(dau:1 eq 1)",
            headers=headers,
        )

        if not response.ok:
            print("Error: {}".format(response.text))
            sys.exit(1)

        for fleet in response.json()["d"]:
            fleets.append((fleet["id"]))

        return fleets

    def get_fleet_metrics(self, fleet_id):
        headers = {
            "Authorization": f"Bearer {BALENA_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"https://api.balena-cloud.com/v6/application({fleet_id})?$expand=owns__device/$count($filter=is_online eq true)",
            headers=headers,
        )

        if not response.ok:
            print("Error: {}".format(response.text))
            sys.exit(1)

        device_online_count = response.json()["d"][0]["owns__device"]
        fleet_name = response.json()["d"][0]["app_name"]

        return fleet_name, device_online_count

    def collect(self):
        gauge = GaugeMetricFamily(
            "balena_devices_online", "Devices by status", labels=["fleet_name"]
        )

        for fleet_id in self.get_balena_fleets():
            fleet_name, device_online_count = self.get_fleet_metrics(str(fleet_id))

            gauge.add_metric([fleet_name], float(device_online_count))

        return [gauge]


def main():
    if not BALENA_TOKEN:
        print("Please set the BALENA_TOKEN environment variable")
        sys.exit(1)

    start_http_server(8000)
    REGISTRY.register(BalenaCollector())
    while True:
        time.sleep(int(CRAWL_INTERVAL))


if __name__ == "__main__":
    main()
