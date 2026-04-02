# 👁️ God View: OS Kernel Telemetry HUD v1.0

A high-performance, dual-layer system monitoring tool that bridges **C++ Global Hooks** with **Python Forensic Analysis**. This project provides a "God-View" into the Windows OS, intercepting hardware signals, NTFS Master File Table modifications, and process lifecycle events in real-time. 

Recently upgraded to a **Unified Control Center** with dynamic thread management, allowing seamless switching between different forensic lenses without crashing the kernel hooks.

## 💡 Why I Built This (The Motivation)

When you build an IoT project or a mechanical device, you can physically see how it works. You can watch the gears turn, trace the wires, and measure the voltage across a circuit. Hardware is tangible and honest. 

But software—especially at the Operating System level—is treated like a black box. When you double-click an app or create a new folder, it just *happens* instantly on your screen as if by magic. 

**I don't like magic. I wanted to see the digital gears turning.**

I built this God-View HUD because I have the exact same curiosity for software architecture that I do for physical machines. I wanted to rip the lid off the Windows OS and watch the Kernel think in real-time. This project is my way of making the invisible, backend mechanics of a computer just as visible, raw, and understandable as a mechanical engine.

## 🚀 Features

### 1. 🎛️ Unified God View Architecture
*   **Thread Manager:** Dynamically spins up and assassinates background listener threads (WMI, Win32 I/O, NTFS Journals) on the fly as you switch modules.
*   **Color-Coded Terminal HUD:** A sleek, borderless, always-on-top translucent UI tracking signals (Green), allocations (Cyan), and process deaths (Magenta).

### 2. 🖱️ Refresh Forensics (Explorer IO Telemetry)
*   **Signal Interception:** Catches physical mouse interrupt requests (IRQs) and maps them to virtual desktop clicks.
*   **DWM Repaint Tracing:** Traces `explorer.exe`'s IO operations, RAM allocations, and CPU Core loads before and after a desktop refresh.
*   **Execution Pipeline:** Visualizes the exact moment the Desktop Window Manager (DWM) repaints the GPU Framebuffer.

### 3. 📁 Folder Creation Forensics (NTFS MFT Telemetry)
*   **Global Multi-Drive Hooking:** Automatically detects all physical drives (C:\, D:\, E:\, etc.) and hooks directly into `ReadDirectoryChangesW` to bypass standard OS delays.
*   **IRP & Kernel Transition:** Tracks the generation of I/O Request Packets (IRP_MJ_CREATE) passed down to `Ntfs.sys`.
*   **MFT & Sector Mapping:** Visualizes the exact Master File Table ($INDEX_ROOT) allocation and Logical Cluster Number (LCN) assignment on the physical disk.
*   **Rename Queueing:** Employs a memory buffer to seamlessly track the transition from `New folder` to a user-defined name before compiling the forensic report.

### 4. ⚙️ App Execution Forensics (Boot & Teardown)
*   **The PE Loader Pipeline:** Traces the lifecycle of an executable being mapped from physical disk into Virtual RAM, including dynamic linking (`ntdll.dll`, `user32.dll`) and CPU thread handoffs.
*   **Strict User-App Filter (Parent Traversal):** Employs an advanced filter that traverses process family trees to silently ignore OS background noise, scheduled tasks, and ghost processes, strictly logging user-initiated apps.
*   **The Execution Reaper (Teardown):** Hooks `Win32_Process` Deletion events to intercept app terminations. Maps thread annihilation, handle closures, and calculates the exact amount of Megabytes (MB) flushed back to the motherboard's RAM pool.

## 🛠️ Tech Stack
*   **Languages:** Python 3, C++
*   **APIs & Hooks:** Windows Management Instrumentation (WMI), PyWin32 (`win32file`, `win32api`, `win32con`), ETW, ctypes.
*   **Telemetry:** `psutil` for real-time hardware tracking (RAM, IO, CPU Threads).
*   **UI:** Tkinter (Borderless, Alpha-blended, Custom Tagging).

## ⚡ How to Run
1. Ensure you have the required dependencies installed:
   ```bash
   pip install psutil pypiwin32 wmi
2. Run the master control center:
   ```bash
   python god_view.py
3. Select your desired forensic module from the dropdown, hit Launch Module, and watch the Windows Kernel go to work.
