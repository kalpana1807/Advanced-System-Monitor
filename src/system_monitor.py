import json
import os
import platform
import sys
import webbrowser
import psutil

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QDialog,
    QTextEdit,
)

from src.widgets import LineChartWidget
from src.worker import SystemWorker, GPU_AVAILABLE

class SystemMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced System Monitor & Health Dashboard (Pro)")
        self.resize(950, 850)
        self.center_window()

        self.latest_metrics = {}
        self.latest_processes = []
        self.is_logging = False

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QWidget { color: #cdd6f4; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
            QTabWidget::pane { border: 1px solid #313244; background: #1e1e2e; border-radius: 8px; }
            QTabBar::tab { background: #313244; color: #bac2de; padding: 10px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background: #89b4fa; color: #11111b; font-weight: bold; }
            QProgressBar { background-color: #313244; border: none; border-radius: 6px; text-align: center; height: 22px; color: #11111b; font-weight: bold; }
            QProgressBar::chunk { background-color: #a6e3a1; border-radius: 6px; }
            QTableWidget { background-color: #11111b; gridline-color: #313244; border: 1px solid #313244; border-radius: 6px; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; padding: 6px; border: none; font-weight: bold; }
            QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 6px; padding: 10px 20px; }
            QPushButton:hover { background-color: #b4befe; }
            QLineEdit, QComboBox { background-color: #11111b; border: 1px solid #313244; border-radius: 6px; padding: 8px; color: #cdd6f4; }
            QComboBox::drop-down { border: none; }
            
            QComboBox QAbstractItemView {
                background-color: #11111b;
                color: #cdd6f4;
                border: 1px solid #313244;
                selection-background-color: #89b4fa;
                selection-color: #11111b;
                outline: none;
            }

            QMenu { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; padding: 4px; }
            QMenu::item { background-color: transparent; padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #89b4fa; color: #11111b; font-weight: bold; }
            QMenu::separator { height: 1px; background: #313244; margin: 4px 0px; }

            QMessageBox { background-color: #1e1e2e; color: #cdd6f4; }
            QMessageBox QLabel { color: #cdd6f4; background-color: transparent; }
            QMessageBox QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 6px; padding: 6px 16px; min-width: 70px; }
            QMessageBox QPushButton:hover { background-color: #b4befe; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = QWidget()
        self.charts_tab = QWidget()
        self.network_tab = QWidget()
        self.gpu_tab = QWidget()
        self.hardware_tab = QWidget()
        self.process_tab = QWidget()

        self.tabs.addTab(self.dashboard_tab, "System Overview")
        self.tabs.addTab(self.charts_tab, "Performance Charts")
        self.tabs.addTab(self.network_tab, "Network & Disk I/O")
        self.tabs.addTab(self.gpu_tab, "GPU Sensors")
        self.tabs.addTab(self.hardware_tab, "Hardware Info")
        self.tabs.addTab(self.process_tab, "Active Processes")

        self.worker = SystemWorker()
        self.worker.data_ready.connect(self.update_ui_data)
        self.worker.start()

        self.init_dashboard_ui()
        self.init_charts_ui()
        self.init_network_ui()
        self.init_gpu_ui()
        self.init_hardware_ui()
        self.init_process_ui()

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def init_dashboard_ui(self):
        layout = QVBoxLayout(self.dashboard_tab)
        layout.setSpacing(15)

        self.health_banner = QLabel("🟢 System Status: Normal & Healthy")
        self.health_banner.setStyleSheet("background-color: #11111b; color: #a6e3a1; border: 1px solid #313244; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.health_banner)

        drive_layout = QHBoxLayout()
        drive_label = QLabel("<b>Select Target Storage Drive:</b>")
        self.drive_combo = QComboBox()
        
        try:
            partitions = psutil.disk_partitions()
            for p in partitions:
                if 'cdrom' in p.opts or p.fstype == '':
                    continue
                self.drive_combo.addItem(f"{p.device} ({p.fstype})", p.mountpoint)
        except Exception:
            self.drive_combo.addItem("C:\\", "C:\\")

        self.drive_combo.currentIndexChanged.connect(self.on_drive_changed)
        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.drive_combo)
        layout.addLayout(drive_layout)

        self.cpu_label = QLabel("CPU Usage: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)

        self.ram_label = QLabel("Memory (RAM) Usage: 0%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.ram_bar)

        self.disk_label = QLabel("Disk Usage: 0%")
        self.disk_bar = QProgressBar()
        self.disk_bar.setMaximum(100)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.disk_bar)

        self.export_btn = QPushButton("Export System Report (JSON)")
        self.export_btn.clicked.connect(self.export_report)
        layout.addWidget(self.export_btn)

        self.log_btn = QPushButton("📊 Start Background CSV Logging")
        self.log_btn.clicked.connect(self.toggle_logging)
        layout.addWidget(self.log_btn)

        layout.addStretch()

    def on_drive_changed(self, index):
        mountpoint = self.drive_combo.itemData(index)
        if mountpoint:
            self.worker.set_target_drive(mountpoint)

    def init_charts_ui(self):
        layout = QVBoxLayout(self.charts_tab)
        layout.setSpacing(20)

        self.cpu_chart = LineChartWidget("CPU History (%)", QColor("#f38ba8"))
        self.ram_chart = LineChartWidget("Memory (RAM) History (%)", QColor("#a6e3a1"))

        layout.addWidget(self.cpu_chart)
        layout.addWidget(self.ram_chart)
        layout.addStretch()

    def init_network_ui(self):
        layout = QVBoxLayout(self.network_tab)
        layout.setSpacing(20)

        self.net_down_label = QLabel("Download Speed: 0 KB/s")
        self.net_up_label = QLabel("Upload Speed: 0 KB/s")
        self.disk_read_label = QLabel("Disk Read Throughput: 0 KB/s")
        self.disk_write_label = QLabel("Disk Write Throughput: 0 KB/s")

        layout.addWidget(self.net_down_label)
        layout.addWidget(self.net_up_label)
        layout.addWidget(self.disk_read_label)
        layout.addWidget(self.disk_write_label)

        layout.addStretch()

    def init_gpu_ui(self):
        layout = QVBoxLayout(self.gpu_tab)
        layout.setSpacing(15)

        self.gpu_status_label = QLabel("<b>GPU Status:</b> Checking availability...")
        layout.addWidget(self.gpu_status_label)

        self.gpu_load_label = QLabel("GPU Core Usage: 0%")
        self.gpu_bar = QProgressBar()
        self.gpu_bar.setMaximum(100)
        layout.addWidget(self.gpu_load_label)
        layout.addWidget(self.gpu_bar)

        self.gpu_vram_label = QLabel("GPU VRAM Usage: 0 MB / 0 MB")
        self.gpu_vram_bar = QProgressBar()
        self.gpu_vram_bar.setMaximum(100)
        layout.addWidget(self.gpu_vram_label)
        layout.addWidget(self.gpu_vram_bar)

        self.gpu_temp_label = QLabel("<b>GPU Temperature:</b> N/A")
        layout.addWidget(self.gpu_temp_label)

        layout.addWidget(QLabel("<hr style='border: 1px solid #313244;'><b>Hardware Sensor Temperatures:</b>"))
        self.sensors_label = QLabel("Scanning core temperature sensors...")
        self.sensors_label.setWordWrap(True)
        layout.addWidget(self.sensors_label)

        layout.addStretch()

    def init_hardware_ui(self):
        layout = QVBoxLayout(self.hardware_tab)
        layout.setSpacing(15)

        uname = platform.uname()
        total_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        cpu_cores = psutil.cpu_count(logical=True)

        layout.addWidget(QLabel(f"<b>Operating System:</b> {uname.system} {uname.release} ({uname.version})"))
        layout.addWidget(QLabel(f"<b>Computer Hostname:</b> {uname.node}"))
        layout.addWidget(QLabel(f"<b>Processor Architecture:</b> {uname.machine} ({uname.processor or 'Standard'})"))
        layout.addWidget(QLabel(f"<b>CPU Cores (Logical):</b> {cpu_cores}"))
        layout.addWidget(QLabel(f"<b>Total Physical RAM:</b> {total_ram_gb} GB"))
        layout.addWidget(QLabel(f"<b>Python Version:</b> {platform.python_version()}"))

        layout.addStretch()

    def init_process_ui(self):
        layout = QVBoxLayout(self.process_tab)
        layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search process by name (e.g. chrome, python)... Double-click any row to inspect!")
        self.search_input.textChanged.connect(self.filter_processes)
        layout.addWidget(self.search_input)

        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["PID", "Process Name", "CPU %", "Memory (MB)"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Context menu
        self.process_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.process_table.customContextMenuRequested.connect(self.show_context_menu)
        self.process_table.viewport().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.process_table.viewport().customContextMenuRequested.connect(self.show_context_menu)

        # Double-click inspection listener
        self.process_table.itemDoubleClicked.connect(self.inspect_process_from_item)

        layout.addWidget(self.process_table)

    def update_ui_data(self, metrics: dict, processes: list):
        self.latest_metrics = metrics
        self.latest_processes = processes

        cpu_val = metrics['cpu']
        ram_val = metrics['ram_percent']

        if cpu_val > 85.0 or ram_val > 90.0 or metrics['gpu_temp'] > 85.0:
            self.health_banner.setText(f"⚠️ High Load Warning! (CPU: {cpu_val}%, RAM: {ram_val}%, GPU Temp: {metrics['gpu_temp']}°C)")
            self.health_banner.setStyleSheet("background-color: #3b1c2b; color: #f38ba8; border: 1px solid #f38ba8; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px;")
        else:
            self.health_banner.setText("🟢 System Status: Normal & Healthy")
            self.health_banner.setStyleSheet("background-color: #11111b; color: #a6e3a1; border: 1px solid #313244; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px;")

        self.cpu_label.setText(f"CPU Usage: {cpu_val}%")
        self.cpu_bar.setValue(int(cpu_val))

        self.ram_label.setText(f"Memory (RAM) Usage: {ram_val}% ({metrics['ram_used']} MB / {metrics['ram_total']} MB)")
        self.ram_bar.setValue(int(ram_val))

        selected_drive = self.drive_combo.currentText() if hasattr(self, 'drive_combo') else "Drive"
        self.disk_label.setText(f"Disk Usage ({selected_drive}): {metrics['disk_percent']}% ({metrics['disk_used']} GB / {metrics['disk_total']} GB)")
        self.disk_bar.setValue(int(metrics['disk_percent']))

        self.cpu_chart.update_data(cpu_val)
        self.ram_chart.update_data(ram_val)

        self.net_down_label.setText(f"Download Speed: {metrics['download_kb']} KB/s")
        self.net_up_label.setText(f"Upload Speed: {metrics['upload_kb']} KB/s")
        self.disk_read_label.setText(f"Disk Read Throughput: {metrics['disk_read_kb']} KB/s")
        self.disk_write_label.setText(f"Disk Write Throughput: {metrics['disk_write_kb']} KB/s")

        if GPU_AVAILABLE and metrics['gpu_mem_total'] > 0:
            self.gpu_status_label.setText("<b>GPU Status:</b> Active NVIDIA GPU Detected")
            self.gpu_load_label.setText(f"GPU Core Usage: {metrics['gpu_load']}%")
            self.gpu_bar.setValue(int(metrics['gpu_load']))
            
            vram_percent = int((metrics['gpu_mem_used'] / metrics['gpu_mem_total']) * 100)
            self.gpu_vram_label.setText(f"GPU VRAM Usage: {metrics['gpu_mem_used']} MB / {metrics['gpu_mem_total']} MB ({vram_percent}%)")
            self.gpu_vram_bar.setValue(vram_percent)
            self.gpu_temp_label.setText(f"<b>GPU Temperature:</b> {metrics['gpu_temp']}°C")
        else:
            self.gpu_status_label.setText("<b>GPU Status:</b> No dedicated NVIDIA GPU found or GPUtil inactive.")

        if metrics['temperatures']:
            self.sensors_label.setText("\n".join(metrics['temperatures']))
        else:
            self.sensors_label.setText("No hardware temperature sensors reported by psutil.")

        self.populate_process_table(processes)

    def populate_process_table(self, processes: list):
        filter_text = self.search_input.text().lower().strip()
        filtered_processes = [
            p for p in processes if filter_text in p[1].lower() or filter_text in str(p[0])
        ]

        self.process_table.setRowCount(len(filtered_processes))
        for row_idx, proc in enumerate(filtered_processes):
            self.process_table.setItem(row_idx, 0, QTableWidgetItem(str(proc[0])))
            self.process_table.setItem(row_idx, 1, QTableWidgetItem(proc[1]))
            self.process_table.setItem(row_idx, 2, QTableWidgetItem(f"{proc[2]}%"))
            self.process_table.setItem(row_idx, 3, QTableWidgetItem(f"{proc[3]} MB"))

    def filter_processes(self):
        self.populate_process_table(self.latest_processes)

    def inspect_process_from_item(self, item):
        row = item.row()
        pid_item = self.process_table.item(row, 0)
        if pid_item:
            pid = int(pid_item.text())
            self.open_process_inspection_modal(pid)

    def open_process_inspection_modal(self, pid: int):
        try:
            p = psutil.Process(pid)
            name = p.name()
            status = p.status()
            exe = p.exe() if hasattr(p, 'exe') else "Access Restricted"
            cwd = p.cwd() if hasattr(p, 'cwd') else "Access Restricted"
            username = p.username() if hasattr(p, 'username') else "N/A"
            create_time = p.create_time() if hasattr(p, 'create_time') else 0
            num_threads = p.num_threads() if hasattr(p, 'num_threads') else "N/A"
            cmdline = " ".join(p.cmdline()) if hasattr(p, 'cmdline') else "N/A"
        except Exception as e:
            QMessageBox.critical(self, "Inspection Error", f"Could not retrieve process details: {str(e)}")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Process Inspector - {name} (PID: {pid})")
        dialog.resize(550, 450)
        dialog.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; }
            QLabel { color: #cdd6f4; font-size: 13px; }
            QTextEdit { background-color: #11111b; color: #a6e3a1; border: 1px solid #313244; border-radius: 6px; font-family: 'Consolas', monospace; font-size: 12px; }
            QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #b4befe; }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)

        layout.addWidget(QLabel(f"<b>Process Name:</b> {name}"))
        layout.addWidget(QLabel(f"<b>Process ID (PID):</b> {pid}"))
        layout.addWidget(QLabel(f"<b>Status:</b> {status}"))
        layout.addWidget(QLabel(f"<b>Owner User:</b> {username}"))
        layout.addWidget(QLabel(f"<b>Active Threads:</b> {num_threads}"))
        layout.addWidget(QLabel(f"<b>Executable Path:</b> {exe}"))
        layout.addWidget(QLabel(f"<b>Working Directory:</b> {cwd}"))
        
        layout.addWidget(QLabel("<b>Command-Line Arguments:</b>"))
        cmd_box = QTextEdit()
        cmd_box.setReadOnly(True)
        cmd_box.setText(cmdline if cmdline.strip() else "None / Internal System Process")
        layout.addWidget(cmd_box)

        close_btn = QPushButton("Close Inspector")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def show_context_menu(self, pos):
        global_pos = self.process_table.viewport().mapToGlobal(pos) if isinstance(self.sender(), QTableWidget) else self.process_table.mapToGlobal(pos)
        row = self.process_table.rowAt(self.process_table.viewport().mapFromGlobal(global_pos).y())
        if row < 0:
            return

        pid_item = self.process_table.item(row, 0)
        name_item = self.process_table.item(row, 1)
        if not pid_item or not name_item:
            return

        pid = int(pid_item.text())
        proc_name = name_item.text()

        menu = QMenu(self)

        inspect_action = QAction(f"🔍 Inspect Process Details ({proc_name})", self)
        inspect_action.triggered.connect(lambda: self.open_process_inspection_modal(pid))
        menu.addAction(inspect_action)

        menu.addSeparator()

        terminate_action = QAction(f"🛑 Terminate Process ({proc_name} - {pid})", self)
        terminate_action.triggered.connect(lambda: self.terminate_process(pid, proc_name))
        menu.addAction(terminate_action)

        menu.addSeparator()

        priority_menu = menu.addMenu("⚙️ Set Priority")
        priorities = [
            ("Idle (Low)", psutil.IDLE_PRIORITY_CLASS if platform.system() == "Windows" else 19),
            ("Below Normal", psutil.BELOW_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 10),
            ("Normal", psutil.NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 0),
            ("Above Normal", psutil.ABOVE_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else -5),
            ("High", psutil.HIGH_PRIORITY_CLASS if platform.system() == "Windows" else -10),
        ]

        for label_text, p_val in priorities:
            p_action = QAction(label_text, self)
            p_action.triggered.connect(lambda checked, val=p_val: self.set_process_priority(pid, proc_name, val))
            priority_menu.addAction(p_action)

        menu.addSeparator()

        folder_action = QAction("📂 Open File Location", self)
        folder_action.triggered.connect(lambda: self.open_process_location(pid, proc_name))
        menu.addAction(folder_action)

        search_action = QAction(f"🔍 Search Process Online ({proc_name})", self)
        search_action.triggered.connect(lambda: webbrowser.open(f"https://www.google.com/search?q={proc_name}+process+windows"))
        menu.addAction(search_action)

        menu.exec(global_pos)

    def terminate_process(self, pid: int, name: str):
        reply = QMessageBox.warning(
            self,
            "Confirm Termination",
            f"Are you sure you want to terminate process '{name}' (PID: {pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                p = psutil.Process(pid)
                p.terminate()
                QMessageBox.information(self, "Success", f"Process {name} terminated.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed: {str(e)}")

    def set_process_priority(self, pid: int, name: str, priority):
        try:
            p = psutil.Process(pid)
            p.nice(priority)
            QMessageBox.information(self, "Success", f"Priority for '{name}' (PID: {pid}) updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set priority: {str(e)}")

    def open_process_location(self, pid: int, name: str):
        try:
            p = psutil.Process(pid)
            exe_path = p.exe()
            if exe_path and os.path.exists(exe_path):
                folder_path = os.path.dirname(exe_path)
                os.startfile(folder_path)
            else:
                QMessageBox.warning(self, "Path Not Found", f"Could not retrieve file path for {name}.")
        except Exception as e:
            QMessageBox.critical(self, "Access Denied", f"Unable to open location: {str(e)}")

    def toggle_logging(self):
        self.is_logging = not self.is_logging
        self.worker.set_logging(self.is_logging)
        if self.is_logging:
            self.log_btn.setText("⏹️ Stop Background CSV Logging")
            self.log_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; font-weight: bold; border-radius: 6px; padding: 10px 20px;")
            QMessageBox.information(self, "Logging Started", "Performance data is now being recorded to 'system_performance_log.csv'.")
        else:
            self.log_btn.setText("📊 Start Background CSV Logging")
            self.log_btn.setStyleSheet("background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 6px; padding: 10px 20px;")
            QMessageBox.information(self, "Logging Stopped", "CSV log file saved successfully.")

    def export_report(self):
        report_data = {
            "metrics": self.latest_metrics,
            "top_processes": [{"pid": p[0], "name": p[1], "cpu_percent": p[2], "memory_mb": p[3]} for p in self.latest_processes]
        }
        try:
            with open("system_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4)
            QMessageBox.information(self, "Export Successful", "Report saved to system_report.json!")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = SystemMonitorApp()
    monitor.show()
    monitor.raise_()
    monitor.activateWindow()
    sys.exit(app.exec())