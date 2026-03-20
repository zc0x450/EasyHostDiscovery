from typing import List


async def discover(
    *,
    targets: str,
    proto: str,
    port: int,
    timeout: float,
    concurrency: int,
) -> List[str]:
    # 第一步占位：后面逐协议（ICMP/TCP/UDP/ARP）实现
    return []
