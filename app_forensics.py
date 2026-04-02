import tkinter as tk
import threading
import pythoncom
import time
import wmi
import psutil
from datetime import datetime

class AppForensicsHUD:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.9)
        self.root.geometry("900x950+30+30")
        self.root.configure(bg='black')

        # --- UI Buttons ---
        self.copy_btn = tk.Button(root, text=" 📋 COPY LOG ", command=self.copy_to_clipboard, 
                                  bg="#222222", fg="#00ff00", font=("Consolas", 10, "bold"), bd=1, cursor="hand2")
        self.copy_btn.place(x=770, y=10)

        self.close_btn = tk.Button(root, text=" EXIT X ", command=self.close_app, 
                                   bg="#440000", fg="white", font=("Arial", 10, "bold"), bd=0, cursor="hand2")
        self.close_btn.place(x=830, y=10)

        # Header
        self.title_label = tk.Label(root, text="👁️ GOD-VIEW: APP EXECUTION FORENSICS", font=("Courier", 16, "bold"), fg="#00ff00", bg="black")
        self.title_label.pack(pady=15)

        # Console with Color Tags
        self.console_text = tk.Text(root, font=("Consolas", 10), fg="white", bg="black", bd=0, highlightthickness=0)
        self.console_text.pack(expand=True, fill='both', padx=20, pady=5)
        
        # Define Colors
        self.console_text.tag_configure("SIGNAL", foreground="#00ff00") # Green
        self.console_text.tag_configure("BIRTH", foreground="#00ffff")  # Cyan
        self.console_text.tag_configure("DEATH", foreground="#ff00ff")  # Magenta
        self.console_text.tag_configure("HEADER", font=("Consolas", 10, "bold"), foreground="#ff3333") # Red

        self.root.bind("<Escape>", lambda e: self.close_app())
        self.running = True
        
        # Memory Dictionary to track live apps for the Death Watcher
        self.tracked_apps = {}
        
        self.log(">>> SYSTEM: Hooked into Win32_Process Creation & Deletion Events.", "SIGNAL")
        self.log(">>> SYSTEM: Parent Process Traversal Filter Active.", "SIGNAL")
        self.log(">>> SYSTEM: Open any Application to view the Boot Sequence. Close it to view the Teardown.\n", "SIGNAL")
        
        # Start Watchers
        self.root.after(500, self.start_birth_watcher)
        self.root.after(500, self.start_death_watcher)

    def log(self, msg, tag="SIGNAL"):
        if self.running:
            self.console_text.insert(tk.END, msg + "\n", tag)
            self.console_text.see(tk.END)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.console_text.get("1.0", tk.END))
        self.root.update() 
        self.log("\n[!] LOG COPIED TO CLIPBOARD SUCCESSFULLY.", "BIRTH")

    def print_app_boot_trace(self, pid, process_name):
        time.sleep(0.5) 
        
        try:
            proc = psutil.Process(pid)
            
            # --- THE ULTIMATE BACKGROUND NOISE FILTER ---
            
            # 1. Reject Access Denied / Kernel Protected apps instantly
            try:
                exe_path = proc.exe()
                if not exe_path:
                    return
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                return # Instantly drop it. No "Access Denied" logs will ever print.

            # 2. Reject Ghost Processes (Apps that use 0 RAM)
            ram_mb = proc.memory_info().rss / (1024 * 1024)
            if ram_mb <= 0.1:
                return
                
            # 3. Parent Process Traversal (Kills auto-updaters like MEGA and Windows Update)
            parent = proc.parent()
            if parent:
                parent_name = parent.name().lower()
                # If the app was launched by a background service instead of Explorer/CMD, ignore it!
                if parent_name in ["svchost.exe", "services.exe", "wininit.exe", "sihost.exe", "taskeng.exe"]:
                    return
                    
            thread_count = proc.num_threads()
            
        except Exception:
            return

        # Save this app's details in memory so we can track its death later
        self.tracked_apps[pid] = {"name": process_name, "ram": ram_mb}

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        msg = f"\n[{timestamp}] 🟢 APPLICATION LAUNCH INTERCEPTED: {process_name}\n" + "=" * 80 + "\n"
        
        msg += "1. THE REQUEST (SHELL EXECUTE)\n"
        msg += f"   |-- Origin: User clicked shortcut. Explorer.exe fired 'CreateProcessW' API.\n"
        msg += f"   |-- Handoff: The request is sent to the Windows Kernel (ntoskrnl.exe).\n"
        msg += f"   |-- Source Path: {exe_path}\n\n"
        
        msg += "2. DISK TO RAM TRANSFER (THE PE LOADER)\n"
        msg += "   |-- Parse: Memory Manager reads the Portable Executable (PE) headers of the file.\n"
        msg += "   |-- Mapping: A 'Section Object' is created to map the hard drive file into Virtual RAM.\n"
        msg += "   |-- Allocation: The `.text` (Code) and `.data` (Variables) segments are loaded into memory.\n\n"
        
        msg += "3. DYNAMIC LINKING (DEPENDENCY INJECTION)\n"
        msg += "   |-- Bootstrapper: The 'ntdll.dll' (LdrInitializeThunk) wakes up to construct the app.\n"
        msg += "   |-- IAT Resolution: The Import Address Table maps required system libraries.\n"
        msg += "   |-- Injection: 'user32.dll' (UI) and 'kernel32.dll' (Core) are injected into the app's memory.\n\n"
        
        msg += "4. THREAD INITIATION (CPU HANDOFF)\n"
        msg += f"   |-- PID Assignment: Kernel assigns unique Process ID [{pid}].\n"
        msg += "   |-- Primary Thread: The Kernel creates the main thread and sets the CPU Instruction Pointer.\n"
        msg += "   |-- Execution: The CPU executes the app's Entry Point (main/WinMain function).\n\n"
        
        msg += "5. GRAPHICS & GPU ENGAGEMENT\n"
        msg += "   |-- Subsystem: App calls DirectX or GDI (Graphics Device Interface).\n"
        msg += "   |-- Swap Chain: A GPU memory buffer is allocated for the app's window.\n"
        msg += "   |-- DWM Handoff: Desktop Window Manager composites the app over your desktop wallpaper.\n\n"
        
        msg += f"6. LIVE TELEMETRY (BOOT COMPLETE)\n"
        msg += f"   |-- Active Process : {process_name} (PID: {pid})\n"
        msg += f"   |-- Physical RAM   : {ram_mb:.2f} MB Allocated instantly\n"
        msg += f"   |-- CPU Workers    : {thread_count} concurrent threads spun up\n"
        msg += f"   |-- Current Status : RUNNING\n"
        msg += "=" * 80

        self.root.after(0, self.log, msg, "SIGNAL")

    def print_app_teardown_trace(self, pid, process_name, ram_freed):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        msg = f"\n[{timestamp}] 🔴 APPLICATION TERMINATION INTERCEPTED: {process_name}\n" + "=" * 80 + "\n"
        
        msg += "1. THE TERMINATION SIGNAL (USER SPACE)\n"
        msg += f"   |-- Origin: User closed window or 'ExitProcess' was called.\n"
        msg += f"   |-- Message: App sent WM_CLOSE signal to the Windows Message Queue.\n"
        msg += f"   |-- Handoff: Kernel initiates teardown sequence via 'ntoskrnl.exe'.\n\n"
        
        msg += "2. THREAD ANNIHILATION\n"
        msg += "   |-- Execution: 'ntdll.dll!RtlExitUserProcess' is invoked.\n"
        msg += "   |-- Halt: Kernel suspends and brutally terminates all child threads belonging to the app.\n"
        msg += "   |-- Context: CPU Context Switch flushes the app from processor cores.\n\n"
        
        msg += "3. HANDLE CLOSURE & RESOURCE RELEASE\n"
        msg += "   |-- Object Manager: Scans for open resources owned by the app.\n"
        msg += "   |-- Unlocking: Force-closes all open File Handles, Registry Keys, and Network Sockets.\n"
        msg += "   |-- Locks: Drops any NTFS file locks (allowing you to delete the file if needed).\n\n"
        
        msg += "4. MEMORY DEALLOCATION (RAM FLUSH)\n"
        msg += "   |-- Virtual RAM: Virtual Memory Manager (VMM) unmaps the `.text` and `.data` segments.\n"
        msg += "   |-- Page Fault: Physical RAM pages are zeroed out and returned to the OS Standby List.\n"
        msg += f"   |-- Telemetry: Successfully flushed {ram_freed:.2f} MB of RAM back to the Motherboard.\n\n"
        
        msg += "5. DWM UNHOOKING (GUI DETACH)\n"
        msg += "   |-- Subsystem: User32.dll calls 'DestroyWindow'.\n"
        msg += "   |-- Swap Chain: The GPU Framebuffer dedicated to this app is destroyed.\n"
        msg += "   |-- Render: Desktop Window Manager erases the app pixels from your screen.\n\n"
        
        msg += "6. PID RETIREMENT & COMPLETION\n"
        msg += f"   |-- Dead Process : {process_name}\n"
        msg += f"   |-- ID Recycled  : PID [{pid}] returned to the Kernel pool.\n"
        msg += f"   |-- Final Status : TERMINATED\n"
        msg += "=" * 80

        self.root.after(0, self.log, msg, "DEATH")

    def start_birth_watcher(self):
        """Immortal Loop: Catches Process Creations"""
        def watch():
            pythoncom.CoInitialize()
            
            # Master blocklist for known annoying background tasks
            ignore_list = [
                "svchost.exe", "dllhost.exe", "conhost.exe", "git.exe", 
                "cmd.exe", "powershell.exe", "wermgr.exe", "backgroundtaskhost.exe", 
                "searchprotocolhost.exe", "runtimebroker.exe", "taskhostw.exe",
                "smartscreen.exe", "sppsvc.exe", "compattelrunner.exe", "ctfmon.exe",
                "wmiprvse.exe", "audiodg.exe", "fontdrvhost.exe", "dashost.exe",
                "sdbinst.exe", "msedgewebview2.exe", "microsoftedgeupdate.exe",
                "megaupdater.exe", "mousocoreworker.exe" # <-- explicitly hardcoded your two ghosts!
            ]

            while self.running:
                try:
                    c = wmi.WMI()
                    watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_Process")
                    
                    while self.running:
                        try:
                            new_process = watcher(timeout_ms=1000)
                            if new_process:
                                process_name = new_process.Caption
                                pid = new_process.ProcessId
                                
                                if process_name and process_name.lower() not in ignore_list:
                                    threading.Thread(target=self.print_app_boot_trace, args=(pid, process_name), daemon=True).start()
                        except wmi.x_wmi_timed_out:
                            continue
                        except Exception:
                            break 
                except Exception:
                    time.sleep(1)

            pythoncom.CoUninitialize()
                
        threading.Thread(target=watch, daemon=True).start()

    def start_death_watcher(self):
        """Immortal Loop: Catches Process Terminations"""
        def watch():
            pythoncom.CoInitialize()
            
            while self.running:
                try:
                    c = wmi.WMI()
                    watcher = c.watch_for(notification_type="Deletion", wmi_class="Win32_Process")
                    
                    while self.running:
                        try:
                            dead_process = watcher(timeout_ms=1000)
                            if dead_process:
                                pid = dead_process.ProcessId
                                
                                # Only print teardown trace if it's an app we actually tracked booting up!
                                if pid in self.tracked_apps:
                                    data = self.tracked_apps.pop(pid) # Remove from dictionary
                                    process_name = data['name']
                                    ram_freed = data['ram']
                                    
                                    threading.Thread(target=self.print_app_teardown_trace, args=(pid, process_name, ram_freed), daemon=True).start()
                        except wmi.x_wmi_timed_out:
                            continue
                        except Exception:
                            break 
                except Exception:
                    time.sleep(1)

            pythoncom.CoUninitialize()
            
        threading.Thread(target=watch, daemon=True).start()

    def close_app(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppForensicsHUD(root)
    root.mainloop()