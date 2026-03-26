from scapy.all import IP, ICMP, sr1


def icmp_ping(ip: str, timeout: float) -> bool:
    # 在线程里调用 scapy（阻塞），如果直接在异步的discovery中调用，会直接把事件循环阻塞住

    pkt = IP(dst=ip) / ICMP()  # 组合数据包，外层是IP协议，内层是ICMP协议
    resp = sr1(
        pkt, timeout=timeout, verbose=0
    )  # 通过sr1函数发送并接收数据包，阻塞等待响应数据包，如果超时则返回None
    # 注意，这里只要响应数据包不为None，就认为主机在线，没有判断收到的ICMP响应包是否是ECHO_REPLY
    return resp is not None
