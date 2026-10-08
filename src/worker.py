import csv
import datetime
import os
import psutil
from PyQt6.QtCore import QThread, pyqtSignal

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class SystemWorker(QThread):
    data_ready = pyqtSignal(dict, list)

    def __init__(self):
        super().__init__()
        self.last_net = psutil.net_io_counters()
        self.last_disk = psutil.disk_io_counters()
        self.logging_enabled = False
        self.target_drive = "C:\\"
        self.csv_file_path = "system_performance_log.csv"

    def set_logging(self, enabled: bool):
        self.logging_enabled = enabled
        if enabled and not os.path.exists(self.csv_file_path):
            try:
                with open(self.csv_file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "CPU %", "RAM %", "RAM Used (MB)", "Disk %", "GPU Load %", "GPU Temp (°C)", "Download (KB/s)", "Upload (KB/s)"])
            except Exception:
                pass

    def set_target_drive(self, drive_path: str):
        self.target_drive = drive_path

    def run(self):
        while True:
            try:
                cpu_usage = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory()
                
                try:
                    disk = psutil.disk_usage(self.target_drive)
                except Exception:
                    disk = psutil.disk_usage("C:\\")

                current_net = psutil.net_io_counters()
                upload_speed = current_net.bytes_sent - self.last_net.bytes_sent
                download_speed = current_net.bytes_recv - self.last_net.bytes_recv
                self.last_net = current_net

                current_disk = psutil.disk_io_counters()
                disk_read = current_disk.read_bytes - self.last_disk.read_bytes if current_disk and self.last_disk else 0
                disk_write = current_disk.write_bytes - self.last_disk.write_bytes if current_disk and self.last_disk else 0
                self.last_disk = current_disk

                gpu_load = 0.0
                gpu_mem_used = 0
                gpu_mem_total = 0
                gpu_temp = 0.0
                if GPU_AVAILABLE:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            gpu_load = gpu.load * 100.0
                            gpu_mem_used = gpu.memoryUsed
                            gpu_mem_total = gpu.memoryTotal
                            gpu_temp = getattr(gpu, 'temperature', 0.0)
                    except Exception:
                        pass

                cpu_temperatures = []
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                cpu_temperatures.append(f"{name} ({getattr(entry, 'label', 'Core')}): {entry.current}°C")
                except Exception:
                    pass

                metrics = {
                    "cpu": cpu_usage,
                    "ram_percent": ram.percent,
                    "ram_used": ram.used // (1024 ** 2),
                    "ram_total": ram.total // (1024 ** 2),
                    "disk_percent": disk.percent,
                    "disk_used": disk.used // (1024 ** 3),
                    "disk_total": disk.total // (1024 ** 3),
                    "upload_kb": upload_speed // 1024,
                    "download_kb": download_speed // 1024,
                    "disk_read_kb": disk_read // 1024,
                    "disk_write_kb": disk_write // 1024,
                    "gpu_load": round(gpu_load, 1),
                    "gpu_mem_used": gpu_mem_used,
                    "gpu_mem_total": gpu_mem_total,
                    "gpu_temp": gpu_temp,
                    "temperatures": cpu_temperatures
                }

                if self.logging_enabled:
                    try:
                        with open(self.csv_file_path, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                cpu_usage,
                                ram.percent,
                                ram.used // (1024 ** 2),
                                disk.percent,
                                round(gpu_load, 1),
                                gpu_temp,
                                upload_speed // 1024,
                                download_speed // 1024
                            ])
                    except Exception:
                        pass

                processes = []
                for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                    try:
                        info = p.info
                        cpu = info['cpu_percent'] or 0.0
                        mem = info['memory_info'].rss // (1024 ** 2) if info['memory_info'] else 0
                        processes.append((info['pid'], info['name'] or "Unknown", cpu, mem))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

                processes.sort(key=lambda x: x[2], reverse=True)
                self.data_ready.emit(metrics, processes)

            except Exception:
                pass

            self.msleep(1000)