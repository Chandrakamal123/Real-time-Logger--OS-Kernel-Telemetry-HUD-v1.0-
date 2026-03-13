import tkinter as tk
import subprocess
import threading
import psutil
import os
import ctypes
import wmi
import pythoncom
from datetime import datetime

class ForensicMarauderHUD:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.9)
        self.root.geometry("900x950+30+30")
        self.root.configure(bg='black')

        # Header
        self.title_label = tk.Label(root, text="👁️ GOD-VIEW: KERNEL FORENSICS", font=("Courier", 16, "bold"), fg="#00ff00", bg="black")
        self.title_label.pack(pady=15)

        # Console with Color Tags
        self.console_text = tk.Text(root, font=("Consolas", 10), fg="white", bg="black", bd=0, highlightthickness=0)
        self.console_text.pack(expand=True, fill='both', padx=20, pady=5)
        
        # Define Colors: Green for Clicks, Cyan for Births, Red for Network
        self.console_text.tag_configure("SIGNAL", foreground="#00ff00") # Green
        self.console_text.tag_configure("BIRTH", foreground="#00ffff")  # Cyan
        self.console_text.tag_configure("NET", foreground="#ff3333")    # Reddish-orange
        self.console_text.tag_configure("HEADER", font=("Consolas", 10, "bold"))

        self.root.bind("<Escape>", lambda e: self.close_app())
        self.running = True
        
        self.start_tracer_engine()      
        self.start_birth_watcher()     

    def log(self, msg, tag="SIGNAL"):
        self.console_text.insert(tk.END, msg + "\n", tag)
        self.console_text.see(tk.END)

    def get_network_info(self, proc):
        """Checks if the process has open internet/network connections."""
        try:
            connections = proc.connections(kind='inet')
            if not connections:
                return "No Active Connections"
            
            # Show the first 2 connections if they exist
            net_list = []
            for conn in connections[:2]:
                l_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                r_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "LISTENING"
                net_list.append(f"{l_addr} -> {r_addr} [{conn.status}]")
            return " | ".join(net_list)
        except:
            return "Access Denied / Not Available"

    def analyze_process(self, pid, event_type="SIGNAL"):
        try:
            proc = psutil.Process(int(pid))
            name = proc.name()
            path = proc.exe()
            
            # 1. Parentage (Who gave birth?)
            try:
                parent = proc.parent().name() if proc.parent() else "System/Kernel"
            except:
                parent = "Unknown"

            # 2. Network Activity
            net_status = self.get_network_info(proc)
            
            # 3. Stats
            mem_mb = proc.memory_info().rss / (1024*1024)
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Formatting the output
            if event_type == "BIRTH":
                header = f"\n[{timestamp}] 🐣 PROCESS BIRTH DETECTED"
                bar = "!" * 80
                tag = "BIRTH"
            else:
                header = f"\n[{timestamp}] 🎯 INTERCEPTED CLICK"
                bar = "=" * 80
                tag = "SIGNAL"

            output = f"{header}\n{bar}\n"
            output += f"⚙️ NAME      : {name} (PID: {pid})\n"
            output += f"👨‍👦 PARENT    : {parent}\n"
            output += f"📂 LOCATION  : {path}\n"
            output += f"🌐 NETWORK   : {net_status}\n"
            output += f"📈 HARDWARE  : {mem_mb:.2f} MB RAM | {proc.num_threads()} Threads\n"
            output += f"{bar}\n"
            
            self.root.after(0, self.log, output, tag)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def start_birth_watcher(self):
        def watch():
            pythoncom.CoInitialize() 
            try:
                c = wmi.WMI()
                watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_Process")
                while self.running:
                    new_process = watcher()
                    self.analyze_process(new_process.ProcessId, event_type="BIRTH")
            except: pass
            finally: pythoncom.CoUninitialize()
        threading.Thread(target=watch, daemon=True).start()

    def start_tracer_engine(self):
        def stream():
            process = subprocess.Popen(['tracer.exe'], stdout=subprocess.PIPE, text=True, bufsize=1)
            for line in process.stdout:
                if "SIGNAL_INTERCEPTED" in line:
                    parts = line.strip().split('|')
                    if len(parts) >= 6:
                        self.analyze_process(parts[5], event_type="SIGNAL")
        threading.Thread(target=stream, daemon=True).start()

    def close_app(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ForensicMarauderHUD(root)
    root.mainloop()