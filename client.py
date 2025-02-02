#!/usr/bin/env python3

from config import Config
from enum import StrEnum, auto
import time
from pathlib import Path
import urllib.request


class PortStatus(StrEnum):
    OK = auto()
    UNABLE_TO_OPEN = auto()
    UNABLE_TO_REACH = auto()
    UNKNOWN_ERROR = auto()


port_status_max_length = max(len(item.value) for item in PortStatus)


class Client:
    def __init__(self):
        self.config = Config()
        (test_port_min, test_port_max) = self.config.client.test_ports
        self.test_port_min = test_port_min
        self.test_port_max = test_port_max
        self.text2open = dict([reversed(i) for i in self.config.open2text.items()])

    def set_test_port(self, test_port: int) -> bool:
        endpoint = f"{self.config.client.server_address}:{self.config.management_port}/{test_port}"
        r = urllib.request.urlopen(endpoint)
        assert r.code == 200
        response_text = r.read().decode().strip().upper()
        is_open = self.text2open[response_text]
        return is_open

    def query_test_port(self, test_port: int) -> bool:
        endpoint = f"{self.config.client.server_address}:{test_port}/"
        try:
            timeout = self.config.client.timeout
            r = urllib.request.urlopen(endpoint, data=None, timeout=timeout)
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                return False
            else:
                raise e
        success = r.code == 200
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
                percent_done = (num_ports_checked / num_ports_to_check) * 100.0
                elapsed = now - start_time
                ports_per_second = num_ports_checked / elapsed
                num_ports_left = num_ports_to_check - num_ports_checked
                time_left = num_ports_left / ports_per_second
                time_left_str = time.strftime("%H:%M:%S", time.gmtime(time_left))
                port_status_str = str(port_status).upper()
                print(
                    f"Port {test_port:5d} - {port_status_str:<{port_status_max_length}s} - {percent_done:5.1f} % done - {time_left_str:>10} left"
                )
                f.write(f"{test_port} {port_status_str}\n")
                time.sleep(self.config.client.sleep_between_requests)


def main() -> None:
    Client().check_ports()


if __name__ == "__main__":
    main()
