import asyncio
import pytest

from easyhostdiscovery import scanner as scanner_mod


def test_discover_tcp_serial_filters_found_ips(monkeypatch) -> None:
    def fake_tcp_connect(ip: str, port: int, timeout: float) -> bool:
        assert port == 80
        return ip in {"127.0.0.1", "127.0.0.2"}

    monkeypatch.setattr(scanner_mod, "tcp_connect", fake_tcp_connect)

    result = asyncio.run(
        scanner_mod.discover(
            targets="127.0.0.0/30",
            proto="tcp",
            port=80,
            timeout=0.2,
            concurrency=10,
            mode="serial",
        )
    )
    assert result == ["127.0.0.1", "127.0.0.2"]


def test_discover_tcp_concurrent_filters_found_ips(monkeypatch) -> None:
    def fake_tcp_connect(ip: str, port: int, timeout: float) -> bool:
        return ip in {"127.0.0.1", "127.0.0.2"}

    monkeypatch.setattr(scanner_mod, "tcp_connect", fake_tcp_connect)

    result = asyncio.run(
        scanner_mod.discover(
            targets="127.0.0.0/30",
            proto="tcp",
            port=1234,
            timeout=0.2,
            concurrency=10,
            mode="concurrent",
        )
    )
    assert result == ["127.0.0.1", "127.0.0.2"]


def test_discover_tcp_invalid_port_raises() -> None:
    with pytest.raises(ValueError):
        asyncio.run(
            scanner_mod.discover(
                targets="127.0.0.1",
                proto="tcp",
                port=0,
                timeout=0.2,
                concurrency=10,
                mode="serial",
            )
        )
