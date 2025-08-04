# utils.py
import platform
import subprocess

def ping_host(ip):
    """Ping host (cross-platform). Returns True if reachable."""
    try:
        if platform.system().lower() == "windows":
            command = ["ping", "-n", "1", "-w", "1000", ip]
        else:
            command = ["ping", "-c", "1", "-W", "1", ip]

        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False
