import socket


def tcp_connect(ip: str, port: int, timeout: float) -> bool:
    try:
        # 这里暂时通过socket来连接目标主机的特定端口，不使用scapy
        s = socket.create_connection((ip, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False
