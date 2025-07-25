import socket

def test_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", port))
        print(f"端口 {port} 可用")
        return True
    except socket.error as e:
        print(f"端口 {port} 被占用或不可用: {e}")
        return False
    finally:
        s.close()

if __name__ == "__main__":
    ports = [8000, 11435]
    for port in ports:
        test_port(port)
    input("\n按Enter键退出...")