#!/usr/bin/env python3

from config import Config
import requests
from enum import StrEnum, auto
import time
from pathlib import Path
import json


class PortStatus(StrEnum):
    OK = auto()
    UNABLE_TO_OPEN = auto()
    UNABLE_TO_REACH = auto()
    UNKNOWN_ERROR = auto()


class Client:
    def __init__(self):
        self.config = Config()
        (test_port_min, test_port_max) = self.config.client.test_ports
        self.test_port_min = test_port_min
        self.test_port_max = test_port_max

    def set_test_port(self, test_port: int) -> bool:
        endpoint = f"{self.config.server.address}:{self.config.management_port}/open/{test_port}"
        r = requests.get(endpoint)
        assert r.status_code == 200
        response = r.json()
        is_open = response["open"]
        return is_open

    def query_test_port(self, test_port: int) -> bool:
        endpoint = f"{self.config.server.address}:{test_port}/"
        try:
            r = requests.get(endpoint, timeout=1)
        except requests.exceptions.Timeout:
            return False
        success = r.status_code == 200
        return success

    def check_port(self, test_port) -> PortStatus:
        if not self.set_test_port(test_port):
            return PortStatus.UNABLE_TO_OPEN
        time.sleep(self.config.client.sleep_between_requests)
        if not self.query_test_port(test_port):
            return PortStatus.UNABLE_TO_REACH
        return PortStatus.OK

    def check_ports(self):
        output_path = Path.cwd() / self.config.client.output_filename
        num_ports_to_check = self.test_port_max - self.test_port_min + 1
        num_ports_checked = 0
        with output_path.open("a") as f:
            start_time = time.time()
            for test_port in range(self.test_port_min, self.test_port_max + 1):
                if test_port == self.config.management_port:
                    continue
                port_status = self.check_port(test_port)
                now = time.time()
                num_ports_checked += 1
                elapsed = now - start_time
                print(
                    f"Port {test_port:5d}: {port_status}. Checked {num_ports_checked} / {num_ports_to_check} Ports in {elapsed} seconds."
                )
                f.write(f"{test_port} {port_status}\n")
                time.sleep(self.config.client.sleep_between_requests)


def main() -> None:
    Client().check_ports()


if __name__ == "__main__":
    main()
