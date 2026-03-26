import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List


async def run_blocking_probe(
    ips: List[str],
    probe: Callable[[str], bool],
    mode: str,
    concurrency: int,
) -> List[str]:
    """在线程池中执行同步 probe(ip)，支持 serial / concurrent。"""
    # 获取通过asyncio.run创建的事件循环
    # 这里不是纯异步代码，因为我们的probe函数是同步的，
    # 我们通过协程来创建并调度任务，实际的任务通过线程池中的线程执行，以此实现并发
    loop = asyncio.get_running_loop()

    if mode == "serial":
        found: List[str] = []  # 用于存储在线的主机IP地址
        with ThreadPoolExecutor(max_workers=1) as executor:
            # 这里设置max_workers=1，确保严格串行执行
            for ip in ips:
                # 把阻塞的函数probe放进线程池中执行，后面跟着的是参数
                # 通过await挂起协程，此时事件循环可以去执行其他协程，调度其他任务
                ok = await loop.run_in_executor(executor, probe, ip)
                if ok:
                    found.append(ip)
        return found

    if mode == "concurrent":
        if concurrency < 1:
            # 避免传入的concurrency参数小于1
            raise ValueError("concurrency must be >= 1")

        sem = asyncio.Semaphore(
            concurrency
        )  # 设置信号量，用于限制通过run_in_executor提交任务的数量
        # 线程池控制同一时间能并发执行的线程数量，是线程级别的限流，而信号量是协程级别的限流
        with ThreadPoolExecutor(max_workers=concurrency) as executor:

            async def worker(ip: str) -> str | None:
                async with sem:
                    # 使用异步上下文管理器，管理信号量的获取和自动释放
                    # 当协程执行到with sem:时，会自动获取信号量，当协程执行完时，会自动释放信号量
                    # 只有获取了信号量的协程才能提交任务
                    ok = await loop.run_in_executor(executor, probe, ip)
                    return ip if ok else None

            # 创建协程任务，每个任务对应一个IP地址
            tasks = [asyncio.create_task(worker(ip)) for ip in ips]
            # 通过gather方法并发执行所有任务，并等待所有任务完成
            results = await asyncio.gather(*tasks)
            # 过滤掉None，只保留在线的主机IP地址
            return [ip for ip in results if ip is not None]

    # 这里其实可以不用加
    raise ValueError("mode must be 'serial' or 'concurrent'")
