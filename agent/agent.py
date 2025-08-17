import argparse
import os
import socket
import time
import json
import psutil
import platform
import shutil
import requests
import configparser
from datetime import datetime, timezone

def load_config():
    """
    Loads config.ini if available, otherwise creates it with defaults.
    """
    cfg = configparser.ConfigParser()
    cfg_path = os.path.join(os.path.dirname(__file__), "config.ini")
    if not os.path.exists(cfg_path):
        cfg["agent"] = {
            "backend_url": "http://127.0.0.1:8000/api/ingest/",
            "api_key": "mysecretkey",
            "interval_seconds": "30"
        }
        with open(cfg_path, "w") as f:
            cfg.write(f)
    else:
        cfg.read(cfg_path)
    return cfg["agent"]

def collect_system_info():
    """
    Collects detailed system information:
    - Hostname, OS details, CPU info, RAM, and storage usage.
    """
    uname = platform.uname()
    svmem = psutil.virtual_memory()
    storage = shutil.disk_usage("/")  # Get root disk usage

    return {
        "name": socket.gethostname(),
        "os": f"{uname.system} {uname.release} {uname.version}",
        "processor": uname.processor,
        "cores": psutil.cpu_count(logical=False),      
        "threads": psutil.cpu_count(logical=True),     
        "ram_gb": round(svmem.total / (1024**3)),      
        "used_ram_gb": round(svmem.used / (1024**3)),  
        "available_ram_gb": round(svmem.available / (1024**3)), 
        "storage_free_gb": round(storage.free / (1024**3)),    
        "storage_total_gb": round(storage.total / (1024**3)),  
        "storage_used_gb": round(storage.used / (1024**3))     
    }

def collect_processes():
    """
    Collects running processes with Task Manager–style CPU usage.
    """
    processes = []

    # Warm up all processes (first call always returns 0.0)
    for proc in psutil.process_iter(['pid']):
        try:
            proc.cpu_percent(interval=None)
        except Exception:
            pass

    # Small delay for accurate % calculations
    time.sleep(0.5)

    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'memory_info']):
        try:
            pinfo = proc.info
            cpu_percent = proc.cpu_percent(interval=None)  # Already system-wide normalized
            mem_mb = round(pinfo['memory_info'].rss / (1024 * 1024), 2)

            # Skip Idle/System process
            if pinfo['pid'] == 0 or (pinfo['name'] and "idle" in pinfo['name'].lower()):
                continue

            processes.append({
                'pid': pinfo['pid'],
                'ppid': pinfo['ppid'],
                'name': pinfo['name'],
                'memory_mb': mem_mb,
                'cpu_percent': round(cpu_percent, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processes


def main():
    """
    Entry point for the monitoring agent.
    Combines CLI args, env vars, and config.ini for flexibility.
    """
    cfg = load_config()

    parser = argparse.ArgumentParser(description='Process Monitoring Agent with System Info')
    
    parser.add_argument('--endpoint', 
                        default=os.getenv('ENDPOINT', cfg.get("backend_url", "http://127.0.0.1:8000/api/ingest/")), 
                        help='Backend ingest endpoint')
    
    parser.add_argument('--api-key', 
                        default=os.getenv('API_KEY', cfg.get("api_key", "mysecretkey")), 
                        help='API key for backend')
    
    parser.add_argument('--hostname', 
                        default=os.getenv('HOSTNAME', socket.gethostname()), 
                        help='Override hostname')
    
    parser.add_argument('--interval', 
                        type=int, 
                        default=int(os.getenv('INTERVAL', cfg.get("interval_seconds", "0"))), 
                        help='If >0, send repeatedly every N seconds')
    
    args = parser.parse_args()

    def send_once():
        """
        Sends a single snapshot of system + process data to the backend.
        """
        print('Collecting System information.........')
        payload = {
            'hostname': args.hostname,
            'reported_at': datetime.now(timezone.utc).isoformat(),
            'system_info': collect_system_info(),
            'processes': collect_processes()
        }
        try:
            resp = requests.post(
                args.endpoint, 
                json=payload, 
                headers={'X-API-Key': args.api_key}, 
                timeout=20
            )
            print(f"POST {args.endpoint} -> {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print('Error sending data:', e)

    if args.interval > 0:
        while True:
            send_once()
            time.sleep(args.interval)
    else:
        send_once()

if __name__ == '__main__':
    main()
