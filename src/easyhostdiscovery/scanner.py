from typing import List

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
    # 在async函数中，可以通过await关键词挂起协程，等待异步操作完成，
    # 在此期间，事件循环可以执行其他协程，提高效率。
    ips = expand_targets(targets)
    # 临时：确认参数能传到扫描层；实现具体协议后这里改为探测并筛选在线主机
    return ips
