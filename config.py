#!/usr/bin/env python3

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    management_port: int = 3000
    test_message: dict[str, str] = field(default_factory=lambda: {"test": "test"})
