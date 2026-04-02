import tkinter as tk
import threading
import psutil
import pythoncom
import time
import wmi
import os
from datetime import datetime

class ForensicMarauderHUD:
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
        self.title_label = tk.Label(root, text="👁️ GOD-VIEW: KERNEL FORENSICS", font=("Courier", 16, "bold"), fg="#00ff00", bg="black")
        self.title_label.pack(pady=15)

        # Console with Color Tags
        self.console_text = tk.Text(root, font=("Consolas", 10), fg="white", bg="black", bd=0, highlightthickness=0)
        self.console_text.pack(expand=True, fill='both', padx=20, pady=5)
        
        # Define Colors
        self.console_text.tag_configure("SIGNAL", foreground="#00ff00") # Green
        self.console_text.tag_configure("BIRTH", foreground="#00ffff")  # Cyan
        self.console_text.tag_configure("HEADER", font=("Consolas", 10, "bold"), foreground="#ff3333") # Red

        self.root.bind("<Escape>", lambda e: self.close_app())
        self.running = True
        
        self.log(">>> SYSTEM: Hooked into OS Telemetry. Waiting for Explorer.exe IO spike...", "SIGNAL")
        self.log(">>> SYSTEM: Initiate Refresh to view detailed trace.\n", "SIGNAL")
        
        # Start Watchers
        self.start_refresh_watcher()      
        self.start_birth_watcher()    

    def log(self, msg, tag="SIGNAL"):
        self.console_text.insert(tk.END, msg + "\n", tag)
        self.console_text.see(tk.END)

    def copy_to_clipboard(self):
        """Copies the entire console text to the clipboard with one click."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.console_text.get("1.0", tk.END))
        self.root.update() # Required for Windows clipboard to register
        self.log("\n[!] LOG COPIED TO CLIPBOARD SUCCESSFULY.", "BIRTH")

    def print_god_view_trace(self, proc, before_io, before_mem, before_cpu_cores):
        """The exact detailed report from your refresh_logger.py"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Give the CPU a fraction of a second to process the refresh 
        time.sleep(0.2) 
        
        try:
            after_io = proc.io_counters().read_count + proc.io_counters().write_count
            after_mem = proc.memory_info().rss / (1024 * 1024)
            after_cpu_cores = psutil.cpu_percent(percpu=True)
        except:
            return

        # Phase 1
        msg1 = f"\n[{timestamp}] 🔴 REFRESH SIGNAL DETECTED\n" + "=" * 60
        self.root.after(0, self.log, msg1, "HEADER")
        time.sleep(0.3)
        
        msg2 = ("1. THE TRIGGER & SIGNAL ROUTING\n"
                "   |-- Origin: Mouse hardware sent a USB Interrupt Request (IRQ) to the Motherboard.\n"
                "   |-- CPU Action: CPU paused current tasks (Context Switch) to read the mouse click.\n"
                "   |-- Kernel Handoff: Windows Kernel (ntoskrnl.exe) translated the physical click into a virtual screen coordinate.\n"
                "   |-- Signal Owner: The signal was handed to User Space -> process 'Explorer.exe'.")
        self.root.after(0, self.log, msg2, "SIGNAL")
        
        # Phase 2
        time.sleep(0.4)
        msg3 = ("\n2. TRANSLATION TO MACHINE LANGUAGE\n"
                "   |-- Note: Windows is pre-compiled. No on-the-fly compiling happens here.\n"
                "   |-- Fetching: Explorer.exe calls the Win32 API (User32.dll).\n"
                "   |-- Machine Code: API commands are broken down into x86-64 Assembly instructions (e.g., MOV, CMP, JMP).\n"
                "   |-- Transport: The Memory Controller moves these instructions from your RAM to the CPU's L1 Instruction Cache.")
        self.root.after(0, self.log, msg3, "SIGNAL")
        
        # Phase 3
        time.sleep(0.4)
        msg4 = (f"\n3. SYSTEM STATE: BEFORE REFRESH\n"
                f"   |-- Explorer IO Operations: {before_io:,}\n"
                f"   |-- Explorer RAM Allocated: {before_mem:.2f} MB\n"
                f"   |-- CPU Core Loads: {before_cpu_cores}")
        self.root.after(0, self.log, msg4, "SIGNAL")
        
        # Phase 4
        time.sleep(0.4)
        msg5 = ("\n4. CPU EXECUTION (THE APPROVAL)\n"
                "   |-- Execution: The CPU's Arithmetic Logic Unit (ALU) executes the instructions.\n"
                "   |-- Action 1: Query the Master File Table (NTFS) to see if Desktop files changed.\n"
                "   |-- Action 2: Recalculate the X and Y grid coordinates for every desktop icon.\n"
                "   |-- Approval: CPU finishes math, flags the Desktop Window Manager (DWM.exe) to repaint.")
        self.root.after(0, self.log, msg5, "SIGNAL")
        
        # Phase 5
        time.sleep(0.4)
        msg6 = (f"\n5. SYSTEM STATE: AFTER REFRESH\n"
                f"   |-- Explorer IO Operations: {after_io:,} (+{after_io - before_io} operations)\n"
                f"   |-- Explorer RAM Allocated: {after_mem:.2f} MB\n"
                f"   |-- CPU Core Loads: {after_cpu_cores}")
        self.root.after(0, self.log, msg6, "SIGNAL")
        
        # Phase 6
        time.sleep(0.4)
        msg7 = ("\n6. THE VISUAL OUTPUT\n"
                "   |-- Render: DWM sends the new pixel map to your GPU Framebuffer.\n"
                "   |-- Display: Your monitor refreshes its pixels (e.g., at 60Hz or 144Hz).\n"
                "   |-- Result: The screen flickers. The refresh is complete.\n" + "=" * 60)
        self.root.after(0, self.log, msg7, "SIGNAL")

    def start_refresh_watcher(self):
        """The exact IO > 10 logic from your refresh_logger.py"""
        def watch():
            last_io = 0
            explorer_proc = None
            
            # Find Explorer once
            for p in psutil.process_iter(['name']):
                if p.info['name'].lower() == 'explorer.exe':
                    explorer_proc = p
                    break
            
            if not explorer_proc: return
            
            while self.running:
                try:
                    counters = explorer_proc.io_counters()
                    current_io = counters.read_count + counters.write_count
                    
                    if last_io != 0 and (current_io - last_io) > 10:
                        before_io = last_io
                        before_mem = explorer_proc.memory_info().rss / (1024 * 1024)
                        before_cpu = psutil.cpu_percent(percpu=True)
                        
                        # Trigger trace in a new thread so the UI stays smooth
                        threading.Thread(target=self.print_god_view_trace, 
                                         args=(explorer_proc, before_io, before_mem, before_cpu), 
                                         daemon=True).start()
                        
                        # Reset baseline
                        counters = explorer_proc.io_counters()
                        last_io = counters.read_count + counters.write_count
                        continue
                        
                    last_io = current_io
                except: pass
                time.sleep(0.1)
                
        threading.Thread(target=watch, daemon=True).start()

    def start_birth_watcher(self):
        def watch():
            pythoncom.CoInitialize() 
            try:
                c = wmi.WMI()
                watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_Process")
                while self.running:
                    new_process = watcher()
                    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    msg = f"[{ts}] 🐣 PROCESS BIRTH DETECTED: {new_process.Caption} (PID: {new_process.ProcessId})"
                    self.root.after(0, self.log, msg, "BIRTH")
            except: pass
            finally: pythoncom.CoUninitialize()
        threading.Thread(target=watch, daemon=True).start()

    def close_app(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ForensicMarauderHUD(root)
    root.mainloop()