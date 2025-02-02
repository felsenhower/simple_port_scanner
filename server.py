#!/usr/bin/env python

import http.server
import socketserver
import threading
from config import Config
import re


def reply(handler, status_code, text):
    handler.send_response(status_code)
    handler.send_header("Content-Type", "text/plain")
    handler.end_headers()
    handler.wfile.write(text.encode())


class PortListener:
    def __init__(self):
        self.config = Config()
        self.current_test_port = None
        self.management_port_http_server = self.create_http_server(
            self.config.management_port, self.ManagementPortHandler
        )

    def create_http_server(self, port, handler):
        server = socketserver.TCPServer(("0.0.0.0", port), handler)
        server.allow_reuse_address = True
        return server

    class ManagementPortHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            try:
                m = re.match(r"^/(\d+)$", self.path)
                new_port = int(m[1])
                success = False
                if new_port == self.server.listener.current_test_port:
                    success = True
                if not success:
                    success = self.server.listener.open_test_port(new_port)
            except Exception as e:
                print(f'Error: "{e}"')
                reply(self, 400, f'Bad Request: "{e}"')
            else:
                response_text = self.server.listener.config.open2text[success]
                reply(self, 200, response_text)

        def log_message(self, format, *args):
            port = self.server.listener.config.management_port
            suffix = " ({}; port={})".format(self.__class__.__name__, port)
            format = format + suffix
            return super().log_message(format, *args)

    class TestPortHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            reply(self, 200, "OK")

        def log_message(self, format, *args):
            port = self.server.listener.current_test_port
            suffix = " ({}; port={})".format(self.__class__.__name__, port)
            format = format + suffix
            return super().log_message(format, *args)

    def open_test_port(self, port):
        if self.current_test_port is not None:
            self.close_test_port()
        try:
            self.http_server_new = self.create_http_server(port, self.TestPortHandler)
            self.http_server_new.listener = self
            self.current_test_port = port
            threading.Thread(
                target=self.http_server_new.serve_forever, daemon=True
            ).start()
            return True
        except Exception as e:
            print(f"Error opening new port {port}: {e}")
            return False

    def close_test_port(self):
        try:
            if self.http_server_new:
                self.http_server_new.shutdown()
                self.current_test_port = None
        except Exception as e:
            print(f"Error closing current port: {e}")

    def listen_on_management_port(self):
        self.management_port_http_server.listener = self
        try:
            self.management_port_http_server.serve_forever()
        finally:
            self.management_port_http_server.server_close()


def main() -> None:
    PortListener().listen_on_management_port()


if __name__ == "__main__":
    main()
