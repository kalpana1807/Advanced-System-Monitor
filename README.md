<<<<<<< HEAD
# 🚀 Advanced System Monitor & Health Dashboard (Pro)

A professional-grade, real-time system performance monitor and health diagnostic dashboard built in **Python** using **PyQt6** and **psutil**. Styled with a gorgeous custom **Catppuccin dark theme**, this tool provides deep hardware metrics, multi-drive storage monitoring, interactive process management controls, and automated audit logging.

---

## ✨ Key Features

- **📊 Real-Time Performance & Custom Charts**: Live tracking and custom-rendered smooth line graphs for CPU and Memory history.
- **💾 Multi-Drive Storage Monitoring**: Dynamically scans all mounted system partitions/drives with live capacity and usage breakdown.
- **📈 Network & Disk Throughput**: Real-time download/upload speeds and disk read/write bandwidth counters.
- **🎮 GPU Sensor Integration**: Live NVIDIA core load, VRAM utilization, and temperature telemetry via `GPUtil`.
- **⚙️ Advanced Process Manager**: Searchable process table with context menus and double-click inspection modals to:
  - **Inspect** deep process details (Executable path, command-line arguments, owner username, thread counts).
  - **Terminate** hanging or resource-heavy processes safely.
  - **Modify Priority** classes on the fly.
  - **Open File Location** or search process definitions online.
- **📁 Audit & Export Capabilities**: Background CSV performance logging (`system_performance_log.csv`) and one-click JSON report exports (`system_report.json`).

---

## 📂 Project Directory Architecture

```text
Advanced-System-Monitor/
│
├── build/                      # PyInstaller build cache
├── installer/                  # Distribution & Inno Setup configuration
│   ├── dist/
│   │   └── system_monitor.exe  # Standalone compiled Windows executable
│   └── setup.iss               # Inno Setup installer script
│
├── src/                        # Source code package
│   ├── __init__.py             # Python package initializer
│   ├── system_monitor.py       # Main application window, UI layout & logic
│   ├── widgets.py              # Custom QWidget real-time rendering charts
│   └── worker.py               # Background QThread for non-blocking telemetry
│
├── system_performance_log.csv  # Background performance logs (generated on toggle)
├── system_report.json          # Exported snapshot report
├── system_monitor.spec         # PyInstaller build specification file
└── README.md                   # Project documentation
🛠️ Prerequisites & Installation
Clone the repository:

git clone [https://github.com/kalpana1807/Advanced-System-Monitor.git](https://github.com/kalpana1807/Advanced-System-Monitor.git)
cd Advanced-System-Monitor

Install required dependencies:
pip install PyQt6 psutil GPUtil

🚀 Running the Application
To run the application directly from the source package while in your project root directory, execute:
python -m src.system_monitor

📦 Building / Executable Deployment
If you want to compile the project into a standalone Windows executable (.exe) using PyInstaller:

pyinstaller system_monitor.spec

=======
# Advanced-System-Monitor
>>>>>>> d7f43e68197d9f2235f438fd37f8aa1dfd634367
