import pytest

from easyhostdiscovery.targets import expand_targets


def test_single_ip() -> None:
    # 测试解析单个IP地址
    assert expand_targets("127.0.0.1") == ["127.0.0.1"]


def test_strips_whitespace() -> None:
    # 测试解析单个IP地址，并去除前后空格
    assert expand_targets("  127.0.0.1  ") == ["127.0.0.1"]


def test_cidr_slash30() -> None:
    # 测试解析网段，返回网段内所有IP地址，去除网段地址和广播地址
    assert expand_targets("10.0.0.0/30") == [
        "10.0.0.1",
        "10.0.0.2",
    ]


def test_empty_raises() -> None:
    # 测试解析空字符串，抛出ValueError
    with pytest.raises(ValueError, match="empty"):
        expand_targets("")


def test_invalid_ip_raises() -> None:
    # 测试解析无效IP地址，抛出ValueError
    with pytest.raises(ValueError):
        expand_targets("not-an-ip")
