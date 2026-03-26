from functools import partial
from typing import List

from .async_runner import run_blocking_probe
from .probes.icmp import icmp_ping
from .probes.tcp import tcp_connect
from .targets import expand_targets


async def discover(
    *,
    targets: str,
    proto: str,
    port: int,
    timeout: float,
    concurrency: int,
    mode: str,
) -> List[str]:
    ips = expand_targets(targets)  # 将目标地址字符串转换为IP地址列表

    timeout_f = float(timeout)
    if timeout_f <= 0:
        # 避免传入的timeout参数小于等于0
        raise ValueError("timeout must be > 0")

    if proto == "icmp":
        # 创建一个偏函数，将timeout参数固定为timeout_f
        probe = partial(icmp_ping, timeout=timeout_f)
        return await run_blocking_probe(ips, probe, mode, concurrency)

    if proto == "tcp":
        if not (1 <= port <= 65535):
            # 避免传入的port参数不在1-65535范围内
            raise ValueError("port must be 1-65535")
        # 创建一个偏函数，将port参数固定为port，timeout参数固定为timeout_f
        probe = partial(tcp_connect, port=port, timeout=timeout_f)
        return await run_blocking_probe(ips, probe, mode, concurrency)

    if proto in ("udp", "arp"):
        # 暂时不支持UDP和ARP协议
        raise NotImplementedError(f"proto={proto!r} not implemented yet")

    raise ValueError(f"unknown proto: {proto!r}")
