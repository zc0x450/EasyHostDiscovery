from __future__ import annotations

import ipaddress
from typing import List


def expand_targets(targets: str) -> List[str]:
    """
    将目标地址字符串转换为IP地址列表
    """
    s = targets.strip()
    if not s:
        # 参数不能为空
        raise ValueError("targets is empty")

    if "/" in s:
        # 解析网段，返回网段内所有IP地址，
        # strict=False允许/前的地址不为网络地址，例如允许192.168.1.1/24
        net = ipaddress.ip_network(s, strict=False)
        return [str(ip) for ip in net.hosts()]  # 去除网段地址和广播地址

    addr = ipaddress.ip_address(s)  # 单个IP地址
    return [str(addr)]
