import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from .targets import expand_targets


def _icmp_ping(ip: str, timeout: float) -> bool:
    # 在线程里调用 scapy（阻塞），如果直接在异步的discovery中调用，会直接把事件循环阻塞住
    from scapy.all import IP, ICMP, sr1

    pkt = IP(dst=ip) / ICMP()  # 组合数据包，外层是IP协议，内层是ICMP协议
    resp = sr1(
        pkt, timeout=timeout, verbose=0
    )  # 通过sr1函数发送并接收数据包，阻塞等待响应数据包，如果超时则返回None
    # 注意，这里只要响应数据包不为None，就认为主机在线，没有判断收到的ICMP响应包是否是ECHO_REPLY
    return resp is not None


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
    # 在此期间，事件循环可以执行其他协程，提高效率
    ips = expand_targets(targets)  # 解析目标地址字符串，返回要扫描的IP地址列表

    if proto != "icmp":
        # 暂时只支持ICMP协议
        raise NotImplementedError("Only proto=icmp implemented yet")

    timeout = float(timeout)
    if timeout <= 0:
        # 避免传入的timeout参数小于等于0
        raise ValueError("timeout must be > 0")

    # 获取通过asyncio.run创建的事件循环
    # 这里不是纯异步代码，因为我们的_icmp_ping函数是同步的，
    # 我们通过协程来创建并调度任务，实际的任务通过线程池中的线程执行，以此实现并发
    loop = asyncio.get_running_loop()

    if mode == "serial":
        found: List[str] = []  # 用于存储在线的主机IP地址
        with ThreadPoolExecutor(max_workers=1) as executor:
            # 这里设置max_workers=1，确保严格串行执行
            for ip in ips:
                # 把阻塞的函数_icmp_ping放进线程池中执行，后面跟着的是参数
                # 通过await挂起协程，此时事件循环可以去执行其他协程，调度其他任务
                ok = await loop.run_in_executor(executor, _icmp_ping, ip, timeout)
                if ok:
                    # 收到的ICMP响应包不为None，认为主机在线
                    found.append(ip)
        return found

    if mode == "concurrent":
        if concurrency < 1:
            # 避免传入的concurrency参数小于1
            raise ValueError("concurrency must be >= 1")

        found: List[str] = []  # 用于存储在线的主机IP地址
        sem = asyncio.Semaphore(
            concurrency
        )  # 设置信号量，用于限制通过run_in_executor提交任务的数量
        # 线程池控制同一时间能并发执行的线程数量，是线程级别的限流，而信号量是协程级别的限流
        with ThreadPoolExecutor(max_workers=concurrency) as executor:

            async def worker(ip: str):
                async with sem:
                    # 使用异步上下文管理器，管理信号量的获取和自动释放
                    # 当协程执行到with sem:时，会自动获取信号量，当协程执行完时，会自动释放信号量
                    # 只有获取了信号量的协程才能提交任务
                    ok = await loop.run_in_executor(executor, _icmp_ping, ip, timeout)
                    return ip if ok else None

            # 创建协程任务，每个任务对应一个IP地址
            tasks = [asyncio.create_task(worker(ip)) for ip in ips]
            # 通过gather方法并发执行所有任务，并等待所有任务完成
            results = await asyncio.gather(*tasks)
            # 过滤掉None，只保留在线的主机IP地址
            return [ip for ip in results if ip is not None]

    # 这里其实可以不用加
    raise ValueError("mode must be 'serial' or 'concurrent'")
