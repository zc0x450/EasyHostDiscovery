import asyncio
import pytest

from easyhostdiscovery import scanner as scanner_mod


# 不使用真实的_icmp_ping，而是伪造一个函数，仅用于验证串行和并发的逻辑是否正确
def test_discover_icmp_serial_filters_found_ips(monkeypatch) -> None:
    def fake_icmp_ping(ip: str, timeout: float) -> bool:
        return ip in {"127.0.0.1", "127.0.0.2"}

    monkeypatch.setattr(scanner_mod, "_icmp_ping", fake_icmp_ping)

    result = asyncio.run(
        scanner_mod.discover(
            targets="127.0.0.0/30",
            proto="icmp",
            port=80,
            timeout=0.2,
            concurrency=20,
            mode="serial",
        )
    )
    assert result == ["127.0.0.1", "127.0.0.2"]


def test_discover_icmp_concurrent_filters_found_ips(monkeypatch) -> None:
    def fake_icmp_ping(ip: str, timeout: float) -> bool:
        return ip in {"127.0.0.1", "127.0.0.2"}

    monkeypatch.setattr(scanner_mod, "_icmp_ping", fake_icmp_ping)

    result = asyncio.run(
        scanner_mod.discover(
            targets="127.0.0.0/30",
            proto="icmp",
            port=80,
            timeout=0.2,
            concurrency=10,
            mode="concurrent",
        )
    )
    assert result == ["127.0.0.1", "127.0.0.2"]


def test_discover_icmp_proto_not_icmp_raises(monkeypatch) -> None:
    # 不用伪造 ping，只验证协议分支
    monkeypatch.setattr(scanner_mod, "_icmp_ping", lambda ip, timeout: True)

    with pytest.raises(NotImplementedError):
        asyncio.run(
            scanner_mod.discover(
                targets="127.0.0.1",
                proto="tcp",
                port=80,
                timeout=0.2,
                concurrency=5,
                mode="serial",
            )
        )
