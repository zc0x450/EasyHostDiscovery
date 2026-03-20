import argparse
import asyncio
from .scanner import discover


def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器
    """
    p = argparse.ArgumentParser(prog="easyhostdiscovery")
    p.add_argument(
        "--targets",
        required=True,
        help="CIDR 或单个 IP（如 192.168.1.0/24 或 192.168.1.10）",
    )
    p.add_argument("--proto", required=True, choices=["icmp", "tcp", "udp", "arp"])
    p.add_argument("--port", type=int, default=80)
    p.add_argument("--timeout", type=float, default=1.0)
    p.add_argument("--concurrency", type=int, default=200)
    p.add_argument(
        "--mode",
        choices=["serial", "concurrent"],
        default="serial",
        help="发现模式：serial 串行 / concurrent 并发",
    )
    return p


async def run_async(args: argparse.Namespace) -> None:
    """
    运行异步主函数
    """
    # 通过await关键字调用异步函数，等待其完成
    hosts = await discover(
        targets=args.targets,
        proto=args.proto,
        port=args.port,
        timeout=args.timeout,
        concurrency=args.concurrency,
        mode=args.mode,
    )
    print(f"discovered_hosts={hosts}")


def main() -> None:
    args = build_parser().parse_args()
    print(f"args={args}")
    # 通过asyncio.run创建事件循环，将run_async创建的协程作为主协程运行，
    # 等待该主协程完成后，关闭事件循环，释放资源
    asyncio.run(run_async(args))
