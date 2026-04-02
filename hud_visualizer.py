import tkinter as tk
import threading
import psutil
import pythoncom
import time
import wmi
import ctypes
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
        self.root.clipboard_clear()
        self.root.clipboard_append(self.console_text.get("1.0", tk.END))
        self.root.update() 
        self.log("\n[!] LOG COPIED TO CLIPBOARD SUCCESSFULY.", "BIRTH")

    def print_god_view_trace(self, proc, before_io, before_mem, before_cpu_cores):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        time.sleep(0.15) 
        
        try:
            after_io = proc.io_counters().read_count + proc.io_counters().write_count
            after_mem = proc.memory_info().rss / (1024 * 1024)
            after_cpu_cores = psutil.cpu_percent(interval=0.1, percpu=True)
        except:
            return

        msg = f"\n[{timestamp}] 🔴 REFRESH SIGNAL DETECTED\n" + "=" * 80 + "\n"
        
        msg += "1. THE TRIGGER & SIGNAL ROUTING\n"
        msg += "   |-- Origin: Mouse hardware sent a USB Interrupt Request (IRQ) to the Motherboard.\n"
        msg += "   |-- CPU Action: CPU paused current tasks (Context Switch) to read the mouse click.\n"
        msg += "   |-- Kernel Handoff: Windows Kernel (ntoskrnl.exe) translated the physical click into a virtual screen coordinate.\n"
        msg += "   |-- Signal Owner: The signal was handed to User Space -> process 'Explorer.exe'.\n\n"
        
        msg += "2. TRANSLATION TO MACHINE LANGUAGE\n"
        msg += "   |-- Note: Windows is pre-compiled. No on-the-fly compiling happens here.\n"
        msg += "   |-- Fetching: Explorer.exe calls the Win32 API (User32.dll).\n"
        msg += "   |-- Machine Code: API commands are broken down into x86-64 Assembly instructions (e.g., MOV, CMP, JMP).\n"
        msg += "   |-- Transport: The Memory Controller moves these instructions from your RAM to the CPU's L1 Instruction Cache.\n\n"
        
        msg += f"3. SYSTEM STATE: BEFORE REFRESH\n"
        msg += f"   |-- Explorer IO Operations: {before_io:,}\n"
        msg += f"   |-- Explorer RAM Allocated: {before_mem:.2f} MB\n"
        msg += f"   |-- CPU Core Loads: {before_cpu_cores}\n\n"
        
        msg += "4. CPU EXECUTION (THE APPROVAL)\n"
        msg += "   |-- Execution: The CPU's Arithmetic Logic Unit (ALU) executes the instructions.\n"
        msg += "   |-- Action 1: Query the Master File Table (NTFS) to see if Desktop files changed.\n"
        msg += "   |-- Action 2: Recalculate the X and Y grid coordinates for every desktop icon.\n"
        msg += "   |-- Approval: CPU finishes math, flags the Desktop Window Manager (DWM.exe) to repaint.\n\n"
        
        msg += f"5. SYSTEM STATE: AFTER REFRESH\n"
        msg += f"   |-- Explorer IO Operations: {after_io:,} (+{after_io - before_io} operations)\n"
        msg += f"   |-- Explorer RAM Allocated: {after_mem:.2f} MB\n"
        msg += f"   |-- CPU Core Loads: {after_cpu_cores}\n\n"
        
        msg += "6. THE VISUAL OUTPUT\n"
        msg += "   |-- Render: DWM sends the new pixel map to your GPU Framebuffer.\n"
        msg += "   |-- Display: Your monitor refreshes its pixels (e.g., at 60Hz or 144Hz).\n"
        msg += "   |-- Result: The screen flickers. The refresh is complete.\n"
        msg += "=" * 80

        self.root.after(0, self.log, msg, "SIGNAL")

    def start_refresh_watcher(self):
        def watch():
            explorer_proc = None
            
            for p in psutil.process_iter(['name']):
                if p.info['name'].lower() == 'explorer.exe':
                    explorer_proc = p
                    break
            
            if not explorer_proc: return
            
            psutil.cpu_percent(percpu=True)
            counters = explorer_proc.io_counters()
            last_io = counters.read_count + counters.write_count
            time.sleep(1) 
            
            last_left_click_time = 0
            
            while self.running:
                try:
                    # STRICT LEFT-CLICK GATE: Only records when Left Mouse Button (0x01) is clicked.
                    # This completely ignores Right-Clicks (0x02) so opening the menu does nothing.
                    if ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000:
                        last_left_click_time = time.time()

                    counters = explorer_proc.io_counters()
                    current_io = counters.read_count + counters.write_count
                    
                    if last_io != 0 and (current_io - last_io) > 10:
                        # Only trigger if the Left click happened recently
                        if (time.time() - last_left_click_time) < 2.0:
                            before_io = last_io
                            before_mem = explorer_proc.memory_info().rss / (1024 * 1024)
                            before_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
                            
                            threading.Thread(target=self.print_god_view_trace, 
                                             args=(explorer_proc, before_io, before_mem, before_cpu), 
                                             daemon=True).start()
                            
                            time.sleep(1.5) # Cooldown
                            
                            counters = explorer_proc.io_counters()
                            last_io = counters.read_count + counters.write_count
                            last_left_click_time = 0 # Consume click
                            continue
                    
                    last_io = current_io
                except: pass
                
                time.sleep(0.05) 
                
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