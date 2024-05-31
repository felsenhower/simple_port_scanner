#!/usr/bin/env python

import http.server
import socketserver
import json
import threading
from urllib.parse import urlparse, parse_qs
from config import Config


def reply(handler, status_code, content_type, text):
    handler.send_response(status_code)
    handler.send_header("Content-Type", content_type)
    handler.end_headers()
    handler.wfile.write(text.encode())


def reply_ok(handler, response):
    reply(handler, 200, "application/json", json.dumps(response))


def reply_error(handler):
    reply(handler, 400, "text/plain  ", "error")


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
        def do_POST(self):
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                message = json.loads(post_data.decode())
                new_port = message["open"]
                success = False
                if new_port == self.server.listener.current_test_port:
                    success = True
                if not success:
                    success = self.server.listener.open_test_port(new_port)
            except:
                reply_error(self)
            else:
                reply_ok(self, {"open": success})

        def log_message(self, format, *args):
            port = self.server.listener.config.management_port
            suffix = " ({}; port={})".format(self.__class__.__name__, port)
            format = format + suffix
            return super().log_message(format, *args)

    class TestPortHandler(http.server.SimpleHTTPRequestHandler):
        def do_POST(self):
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                message = json.loads(post_data.decode())
                if message != self.server.listener.config.test_message:
                    raise ValueError()
            except:
                reply_error(self)
            else:
                reply_ok(self, {"valid": True})

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
