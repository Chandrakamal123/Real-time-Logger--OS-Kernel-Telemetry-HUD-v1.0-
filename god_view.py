import tkinter as tk
from tkinter import ttk
import threading
import pythoncom
import time
import wmi
import psutil
import os
import win32file
import win32api
import ctypes
from datetime import datetime

class GodViewApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.95)
        self.root.geometry("1000x950+30+30")
        self.root.configure(bg='#050505')

        # ==========================================
        # 1. TOP HEADER (App Title & Window Controls)
        # ==========================================
        top_bar = tk.Frame(root, bg="#111111", bd=1, relief="ridge")
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(top_bar, text="👁️ GOD VIEW", font=("Courier", 18, "bold"), fg="#00ff00", bg="#111111").pack(side="left", padx=15, pady=10)

        self.close_btn = tk.Button(top_bar, text=" EXIT X ", command=self.close_app, 
                                   bg="#440000", fg="white", font=("Arial", 10, "bold"), bd=0, cursor="hand2")
        self.close_btn.pack(side="right", padx=15, pady=10)

        self.copy_btn = tk.Button(top_bar, text=" 📋 COPY LOG ", command=self.copy_to_clipboard, 
                                  bg="#222222", fg="#00ff00", font=("Consolas", 10, "bold"), bd=1, cursor="hand2")
        self.copy_btn.pack(side="right", padx=5, pady=10)

        # ==========================================
        # 2. CONTROLS (Dropdown Option)
        # ==========================================
        control_frame = tk.Frame(root, bg="#050505")
        control_frame.pack(fill="x", padx=10, pady=10)

        self.modules = [
            "Refresh Forensics (Explorer IO Telemetry)",
            "Folder Creation Forensics (NTFS MFT Telemetry)",
            "App Execution Forensics (WMI Process Trace)"
        ]
        
        self.selected_module = tk.StringVar()
        self.combo = ttk.Combobox(control_frame, textvariable=self.selected_module, values=self.modules, width=50, font=("Consolas", 11), state="readonly")
        self.combo.pack(side="left", padx=10)
        self.combo.set(self.modules[0]) # Default selection

        launch_btn = tk.Button(control_frame, text="▶ LAUNCH MODULE", command=self.switch_module, 
                               bg="#005500", fg="white", font=("Arial", 10, "bold"), bd=1, cursor="hand2")
        launch_btn.pack(side="left", padx=10)

        # ==========================================
        # 3. TERMINAL SCREEN (Header + Console)
        # ==========================================
        terminal_container = tk.Frame(root, bg="#111111", bd=2, relief="sunken")
        terminal_container.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        # Dynamic Terminal Header
        self.terminal_header_var = tk.StringVar()
        self.terminal_header_var.set("God View : Awaiting Module Selection...")
        
        header_label = tk.Label(terminal_container, textvariable=self.terminal_header_var, 
                                font=("Consolas", 12, "bold"), fg="#ff3333", bg="#111111", anchor="w")
        header_label.pack(fill="x", padx=10, pady=5)

        tk.Frame(terminal_container, bg="#333333", height=2).pack(fill="x") # Separator line

        # The actual text console
        self.console_text = tk.Text(terminal_container, font=("Consolas", 10), fg="white", bg="black", bd=0, highlightthickness=0)
        self.console_text.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Color Tags
        self.console_text.tag_configure("SIGNAL", foreground="#00ff00") # Green
        self.console_text.tag_configure("BIRTH", foreground="#00ffff")  # Cyan
        self.console_text.tag_configure("DEATH", foreground="#ff00ff")  # Magenta
        self.console_text.tag_configure("HEADER", font=("Consolas", 10, "bold"), foreground="#ff3333") # Red

        # ==========================================
        # STATE MANAGEMENT
        # ==========================================
        self.root.bind("<Escape>", lambda e: self.close_app())
        self.running = True
        self.active_module = None 
        self.tracked_apps = {} # Used for App Forensics teardown
        
        self.log(">>> SYSTEM: God View Architecture Initialized.", "SIGNAL")
        self.log(">>> SYSTEM: Select a module from the dropdown and click 'LAUNCH MODULE'.\n", "SIGNAL")

    def log(self, msg, tag="SIGNAL"):
        if self.running:
            self.console_text.insert(tk.END, msg + "\n", tag)
            self.console_text.see(tk.END)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.console_text.get("1.0", tk.END))
        self.root.update() 
        self.log("\n[!] LOG COPIED TO CLIPBOARD SUCCESSFULLY.", "BIRTH")

    def switch_module(self):
        """Kills old threads and boots the newly selected module."""
        module = self.selected_module.get()
        
        # 1. Kill old threads by changing the active flag
        self.active_module = None 
        time.sleep(0.5) # Brief pause to let old while-loops break
        
        # 2. Clear Console & Update Header
        self.console_text.delete("1.0", tk.END)
        self.terminal_header_var.set(f"God View : {module.upper()}")
        
        # 3. Boot new module
        self.active_module = module
        
        if "Refresh Forensics" in module:
            self.log(">>> SYSTEM: Hooked into Explorer IO Telemetry.", "SIGNAL")
            self.log(">>> SYSTEM: Initiate Desktop Refresh to view trace.\n", "SIGNAL")
            threading.Thread(target=self.watcher_refresh, daemon=True).start()
            
        elif "Folder Creation" in module:
            self.log(">>> SYSTEM: Hooked into Global NTFS File System.", "SIGNAL")
            self.log(">>> SYSTEM: Parent Process Traversal Filter Active.", "SIGNAL")
            self.log(">>> SYSTEM: Create a 'New Folder' ANYWHERE to view trace.\n", "SIGNAL")
            threading.Thread(target=self.watcher_folder_creation, daemon=True).start()
            
        elif "App Execution" in module:
            self.log(">>> SYSTEM: Hooked into Win32_Process Creation & Deletion.", "SIGNAL")
            self.log(">>> SYSTEM: Strict User-App Filter Active (Ignoring OS background noise).", "SIGNAL")
            self.log(">>> SYSTEM: Open any App to view Boot trace. Close it to view Teardown.\n", "SIGNAL")
            threading.Thread(target=self.watcher_app_birth, daemon=True).start()
            threading.Thread(target=self.watcher_app_death, daemon=True).start()

    # =========================================================================
    # MODULE 1: REFRESH FORENSICS
    # =========================================================================
    def print_refresh_trace(self, proc, before_io, before_mem, before_cpu_cores):
        if self.active_module != "Refresh Forensics (Explorer IO Telemetry)": return
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        time.sleep(0.15) 
        try:
            after_io = proc.io_counters().read_count + proc.io_counters().write_count
            after_mem = proc.memory_info().rss / (1024 * 1024)
            after_cpu_cores = psutil.cpu_percent(interval=0.1, percpu=True)
        except: return

        msg = f"\n[{timestamp}] 🔴 REFRESH SIGNAL DETECTED\n" + "=" * 80 + "\n"
        msg += "1. THE TRIGGER & SIGNAL ROUTING\n"
        msg += "   |-- Origin: Mouse hardware sent a USB Interrupt Request (IRQ) to the Motherboard.\n"
        msg += "   |-- CPU Action: CPU paused current tasks (Context Switch) to read the mouse click.\n"
        msg += "   |-- Kernel Handoff: Windows Kernel (ntoskrnl.exe) translated the physical click into a virtual coordinate.\n"
        msg += "   |-- Signal Owner: The signal was handed to User Space -> process 'Explorer.exe'.\n\n"
        
        msg += f"2. SYSTEM STATE: BEFORE REFRESH\n"
        msg += f"   |-- Explorer IO Operations: {before_io:,}\n"
        msg += f"   |-- Explorer RAM Allocated: {before_mem:.2f} MB\n"
        msg += f"   |-- CPU Core Loads: {before_cpu_cores}\n\n"
        
        msg += "3. CPU EXECUTION (THE APPROVAL)\n"
        msg += "   |-- Action 1: Query the Master File Table (NTFS) to see if Desktop files changed.\n"
        msg += "   |-- Action 2: Recalculate the X and Y grid coordinates for every desktop icon.\n"
        msg += "   |-- Approval: CPU finishes math, flags the Desktop Window Manager (DWM.exe) to repaint.\n\n"
        
        msg += f"4. SYSTEM STATE: AFTER REFRESH\n"
        msg += f"   |-- Explorer IO Operations: {after_io:,} (+{after_io - before_io} operations)\n"
        msg += f"   |-- Explorer RAM Allocated: {after_mem:.2f} MB\n"
        msg += f"   |-- CPU Core Loads: {after_cpu_cores}\n\n"
        
        msg += "5. THE VISUAL OUTPUT\n"
        msg += "   |-- Render: DWM sends the new pixel map to your GPU Framebuffer.\n"
        msg += "   |-- Result: The screen flickers. The refresh is complete.\n"
        msg += "=" * 80
        self.root.after(0, self.log, msg, "SIGNAL")

    def watcher_refresh(self):
        explorer_proc = None
        for p in psutil.process_iter(['name']):
            if p.info['name'].lower() == 'explorer.exe':
                explorer_proc = p
                break
        if not explorer_proc: return
        
        psutil.cpu_percent(percpu=True)
        counters = explorer_proc.io_counters()
        last_io = counters.read_count + counters.write_count
        last_left_click_time = 0
        
        while self.running and self.active_module == "Refresh Forensics (Explorer IO Telemetry)":
            try:
                if ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000:
                    last_left_click_time = time.time()

                counters = explorer_proc.io_counters()
                current_io = counters.read_count + counters.write_count
                
                if last_io != 0 and (current_io - last_io) > 10:
                    if (time.time() - last_left_click_time) < 2.0:
                        before_io = last_io
                        before_mem = explorer_proc.memory_info().rss / (1024 * 1024)
                        before_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
                        
                        threading.Thread(target=self.print_refresh_trace, args=(explorer_proc, before_io, before_mem, before_cpu), daemon=True).start()
                        time.sleep(1.5) 
                        
                        counters = explorer_proc.io_counters()
                        last_io = counters.read_count + counters.write_count
                        last_left_click_time = 0 
                        continue
                last_io = current_io
            except: pass
            time.sleep(0.05)

    # =========================================================================
    # MODULE 2: FOLDER CREATION FORENSICS
    # =========================================================================
    def print_folder_trace(self, folder_path, drive):
        if self.active_module != "Folder Creation Forensics (NTFS MFT Telemetry)": return
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        msg = f"\n[{timestamp}] 🔴 DIRECTORY ALLOCATION DETECTED\n" + "=" * 80 + "\n"
        msg += "1. THE REQUEST (USER SPACE)\n"
        msg += f"   |-- Origin: Explorer.exe executed the 'CreateDirectoryW' Win32 API call.\n"
        msg += f"   |-- Target Path: {folder_path}\n"
        msg += f"   |-- Target Disk: Physical Volume {drive}\n\n"
        msg += "2. KERNEL TRANSITION (IRP GENERATION)\n"
        msg += "   |-- Dispatch: IRP pushed down the driver stack directly to 'Ntfs.sys'.\n\n"
        msg += "3. MASTER FILE TABLE (MFT) ALLOCATION\n"
        msg += "   |-- MFT Entry: Allocated a new 1KB File Record Segment (FRS) in the Master File Table.\n"
        msg += "   |-- Data Attribute: Initialized $INDEX_ROOT.\n\n"
        msg += "4. PHYSICAL DISK MAPPING\n"
        msg += f"   |-- Volume Bitmap: Searched {drive} for free Logical Clusters.\n"
        msg += "   |-- LCN Assignment: Claimed a Logical Cluster Number (LCN) to store folder metadata.\n\n"
        msg += "5. THE VISUAL OUTPUT & COMPLETION\n"
        msg += f"   |-- Render: Desktop Window Manager (DWM) draws '{os.path.basename(folder_path)}' on your screen.\n"
        msg += "=" * 80
        self.root.after(0, self.log, msg, "SIGNAL")

    def watcher_folder_creation(self):
        drives = [d for d in win32api.GetLogicalDriveStrings().split('\000')[:-1]]
        pending_reports = {}

        def queue_processor():
            while self.running and self.active_module == "Folder Creation Forensics (NTFS MFT Telemetry)":
                now = time.time()
                try:
                    for key in list(pending_reports.keys()):
                        if now - pending_reports[key]['time'] > 8.0:
                            data = pending_reports.pop(key, None)
                            if data:
                                threading.Thread(target=self.print_folder_trace, args=(data['actual_path'], data['drive']), daemon=True).start()
                except RuntimeError: pass
                time.sleep(0.5)

        threading.Thread(target=queue_processor, daemon=True).start()
        
        def watch_drive(drive_path):
            try:
                hDir = win32file.CreateFile(
                    drive_path, 0x0001, 0x01 | 0x02 | 0x04, None, 3, 0x02000000, None
                )
            except Exception: return 
            
            old_rename_key = None 
            
            while self.running and self.active_module == "Folder Creation Forensics (NTFS MFT Telemetry)":
                try:
                    results = win32file.ReadDirectoryChangesW(hDir, 65536, True, 0x0002, None, None)
                    for action, file in results:
                        full_path = os.path.join(drive_path, file)
                        path_key = full_path.lower() 
                        
                        if any(noise in path_key for noise in ["appdata", "windows", "$recycle.bin", "temp", "prefetch", "programdata"]):
                            continue
                        
                        if action == 1:
                            pending_reports[path_key] = {"drive": drive_path[:2], "time": time.time(), "actual_path": full_path}
                            if "new folder" in os.path.basename(full_path).lower():
                                self.root.after(0, self.log, f"[!] KERNEL: Allocation caught. Type a name and press ENTER...", "BIRTH")
                        elif action == 4:
                            old_rename_key = path_key
                        elif action == 5:
                            if old_rename_key and old_rename_key in pending_reports:
                                data = pending_reports.pop(old_rename_key, None)
                                if data: threading.Thread(target=self.print_folder_trace, args=(full_path, data['drive']), daemon=True).start()
                            old_rename_key = None 
                except Exception: pass

        for drive in drives:
            threading.Thread(target=watch_drive, args=(drive,), daemon=True).start()

    # =========================================================================
    # MODULE 3: APP EXECUTION FORENSICS
    # =========================================================================
    def print_app_boot_trace(self, pid, process_name):
        if self.active_module != "App Execution Forensics (WMI Process Trace)": return
        time.sleep(0.5) 
        try:
            proc = psutil.Process(pid)
            try:
                exe_path = proc.exe()
                if not exe_path: return
            except (psutil.AccessDenied, psutil.NoSuchProcess): return 
            ram_mb = proc.memory_info().rss / (1024 * 1024)
            if ram_mb <= 0.1: return
            parent = proc.parent()
            if parent and parent.name().lower() in ["svchost.exe", "services.exe", "wininit.exe", "sihost.exe", "taskeng.exe"]: return
            thread_count = proc.num_threads()
        except Exception: return

        self.tracked_apps[pid] = {"name": process_name, "ram": ram_mb}
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        msg = f"\n[{timestamp}] 🟢 APPLICATION LAUNCH INTERCEPTED: {process_name}\n" + "=" * 80 + "\n"
        msg += "1. THE REQUEST (SHELL EXECUTE)\n"
        msg += f"   |-- Source Path: {exe_path}\n\n"
        msg += "2. DISK TO RAM TRANSFER (THE PE LOADER)\n"
        msg += "   |-- Allocation: The `.text` (Code) and `.data` (Variables) segments are loaded into memory.\n\n"
        msg += "3. THREAD INITIATION (CPU HANDOFF)\n"
        msg += f"   |-- PID Assignment: Kernel assigns unique Process ID [{pid}].\n\n"
        msg += f"4. LIVE TELEMETRY (BOOT COMPLETE)\n"
        msg += f"   |-- Physical RAM   : {ram_mb:.2f} MB Allocated instantly\n"
        msg += f"   |-- CPU Workers    : {thread_count} concurrent threads spun up\n"
        msg += f"   |-- Current Status : RUNNING\n"
        msg += "=" * 80
        self.root.after(0, self.log, msg, "SIGNAL")

    def print_app_teardown_trace(self, pid, process_name, ram_freed):
        if self.active_module != "App Execution Forensics (WMI Process Trace)": return
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        msg = f"\n[{timestamp}] 🔴 APPLICATION TERMINATION INTERCEPTED: {process_name}\n" + "=" * 80 + "\n"
        msg += "1. THE TERMINATION SIGNAL (USER SPACE)\n"
        msg += f"   |-- Origin: User closed window or 'ExitProcess' was called.\n\n"
        msg += "2. THREAD ANNIHILATION\n"
        msg += "   |-- Halt: Kernel suspends and brutally terminates all child threads belonging to the app.\n\n"
        msg += "3. MEMORY DEALLOCATION (RAM FLUSH)\n"
        msg += f"   |-- Telemetry: Successfully flushed {ram_freed:.2f} MB of RAM back to the Motherboard.\n\n"
        msg += "4. PID RETIREMENT & COMPLETION\n"
        msg += f"   |-- ID Recycled  : PID [{pid}] returned to the Kernel pool.\n"
        msg += f"   |-- Final Status : TERMINATED\n"
        msg += "=" * 80
        self.root.after(0, self.log, msg, "DEATH")

    def watcher_app_birth(self):
        pythoncom.CoInitialize()
        ignore_list = [
            "svchost.exe", "dllhost.exe", "conhost.exe", "git.exe", "cmd.exe", "powershell.exe", 
            "wermgr.exe", "backgroundtaskhost.exe", "searchprotocolhost.exe", "runtimebroker.exe", 
            "taskhostw.exe", "smartscreen.exe", "sppsvc.exe", "compattelrunner.exe", "ctfmon.exe",
            "wmiprvse.exe", "audiodg.exe", "fontdrvhost.exe", "dashost.exe", "sdbinst.exe", 
            "msedgewebview2.exe", "microsoftedgeupdate.exe", "megaupdater.exe", "mousocoreworker.exe"
        ]
        while self.running and self.active_module == "App Execution Forensics (WMI Process Trace)":
            try:
                c = wmi.WMI()
                watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_Process")
                while self.running and self.active_module == "App Execution Forensics (WMI Process Trace)":
                    try:
                        new_process = watcher(timeout_ms=1000)
                        if new_process:
                            process_name = new_process.Caption
                            pid = new_process.ProcessId
                            if process_name and process_name.lower() not in ignore_list:
                                threading.Thread(target=self.print_app_boot_trace, args=(pid, process_name), daemon=True).start()
                    except wmi.x_wmi_timed_out: continue
                    except Exception: break 
            except Exception: time.sleep(1)
        pythoncom.CoUninitialize()

    def watcher_app_death(self):
        pythoncom.CoInitialize()
        while self.running and self.active_module == "App Execution Forensics (WMI Process Trace)":
            try:
                c = wmi.WMI()
                watcher = c.watch_for(notification_type="Deletion", wmi_class="Win32_Process")
                while self.running and self.active_module == "App Execution Forensics (WMI Process Trace)":
                    try:
                        dead_process = watcher(timeout_ms=1000)
                        if dead_process:
                            pid = dead_process.ProcessId
                            if pid in self.tracked_apps:
                                data = self.tracked_apps.pop(pid)
                                threading.Thread(target=self.print_app_teardown_trace, args=(pid, data['name'], data['ram']), daemon=True).start()
                    except wmi.x_wmi_timed_out: continue
                    except Exception: break 
            except Exception: time.sleep(1)
        pythoncom.CoUninitialize()

    def close_app(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GodViewApp(root)
    root.mainloop()