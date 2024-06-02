#!/usr/bin/env python3

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClientConfig:
    test_ports: tuple[int, int] = (1, 65535)
    timeout: float = 1
    sleep_between_requests: float = 0.0
    output_filename: str = "ports.txt"


@dataclass(frozen=True)
class ServerConfig:
    address: str = "http://127.0.0.1"


@dataclass(frozen=True)
class Config:
    management_port: int = 3000
    test_message: dict[str, str] = field(default_factory=lambda: {"test": "test"})
    client: ClientConfig = ClientConfig()
    server: ServerConfig = ServerConfig()
