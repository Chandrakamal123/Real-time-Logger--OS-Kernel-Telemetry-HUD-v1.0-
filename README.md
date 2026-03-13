# 👁️ Real-Time Logger: OS Kernel Telemetry HUD v1.0

A high-performance, dual-layer system monitoring tool that bridges **C++ Global Hooks** with **Python Forensic Analysis**. This project provides a "God-View" into the Windows OS, intercepting hardware signals, process lifecycle events, and network sockets in real-time.

---

## 🚀 Features

### 1. The Marauder's Map (Click Interceptor)
* **Global Mouse Hooking**: Uses a C++ Low-Level Hook (`WH_MOUSE_LL`) to intercept signals before they reach the target application.
* **Window DNA**: Identifies the `HWND`, Window Class, and Thread ID of any clicked element (Taskbar, Desktop, or System Apps).

### 2. Process Birth Detection (Spawn Logger)
* **Kernel Event Watcher**: Utilizes Windows Management Instrumentation (WMI) to detect the exact millisecond a new process is born.
* **Lineage Tracing**: Automatically identifies the **Parent Process** to show the chain of command (e.g., `explorer.exe` -> `cmd.exe` -> `python.exe`).

### 3. Forensic Deep-Dive
* **Network Intelligence**: Scans for active IPv4/IPv6 connections and socket statuses (`ESTABLISHED`, `LISTENING`).
* **Hardware Profiling**: Real-time tracking of Memory (RAM) usage and CPU thread counts per process.
* **Security Insight**: Detects UAC elevation status (Admin vs. Standard privileges).

---

## 🏗️ Architecture

The system operates via a **Producer-Consumer** model:
1.  **The Producer (C++)**: `tracer.cpp` compiles into a lightweight background engine that pipes raw hex/system data to `stdout`.
2.  **The Consumer (Python)**: `hud_visualizer.py` acts as a multi-threaded forensic suite, parsing the pipe and performing secondary lookups via `psutil` and `WMI`.

---

## 🛠️ Installation & Setup

### Prerequisites
* **OS**: Windows 10/11
* **Compiler**: MinGW/g++
* **Environment**: Python 3.10+

### 1. Clone & Dependencies
```bash
git clone [https://github.com/Chandrakamal123/Real-time-Logger--OS-Kernel-Telemetry-HUD-v1.0-.git](https://github.com/Chandrakamal123/Real-time-Logger--OS-Kernel-Telemetry-HUD-v1.0-.git)
cd Real-time-Logger
pip install wmi pywin32 psutil

### 2. Compile the Engine
```bash
g++ tracer.cpp -o tracer.exe


### 2. Launch the HUD
```bash
python hud_visualizer.py


### 3. Telemetry Output Example
```bash
[17:46:07.120] 🐣 PROCESS BIRTH DETECTED
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
⚙️ NAME      : chrome.exe (PID: 10212)
👨‍👦 PARENT    : chrome.exe
📂 LOCATION  : C:\Program Files\Google\Chrome\Application\chrome.exe
🌐 NETWORK   : 192.168.1.5:55625 -> 142.250.190.46:443 [ESTABLISHED]
📈 HARDWARE  : 41.00 MB RAM | 14 Threads
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

