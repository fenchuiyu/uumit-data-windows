"""
隧道保活脚本 - 自动重连
运行: python keep_tunnel.py
"""
import subprocess
import time
import sys


def run_tunnel():
    """运行 SSH 隧道，断开后自动重连"""
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=10",
        "-o", "ServerAliveCountMax=3",
        "-o", "TCPKeepAlive=yes",
        "-R", "80:localhost:8000",
        "nokey@localhost.run"
    ]

    retry = 0
    while True:
        retry += 1
        print(f"[{time.strftime('%H:%M:%S')}] 第 {retry} 次连接隧道...")
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # 等 5 秒看隧道是否建立成功
            time.sleep(5)
            if proc.poll() is not None:
                print(f"[{time.strftime('%H:%M:%S')}] 连接失败，{10}秒后重试...")
                time.sleep(10)
                continue
            print(f"[{time.strftime('%H:%M:%S')}] 隧道已建立 (PID: {proc.pid})")
            proc.wait()
            print(f"[{time.strftime('%H:%M:%S')}] 隧道断开，3 秒后重连...")
        except KeyboardInterrupt:
            print("\n已停止")
            sys.exit(0)
        except Exception as e:
            print(f"错误: {e}")
        time.sleep(3)


if __name__ == "__main__":
    print("UUMit 隧道保活脚本启动")
    run_tunnel()
