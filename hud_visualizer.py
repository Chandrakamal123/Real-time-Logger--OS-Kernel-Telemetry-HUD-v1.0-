import tkinter as tk
import subprocess
import threading
import psutil
import time
import os
from datetime import datetime

class GodViewHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("God-View HUD")
        
        # 1. Setup the Transparent, Borderless HUD
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.geometry("650x800+50+50")
        self.root.configure(bg='black')

        # 2. UI Elements
        self.title_label = tk.Label(root, text="👁️ SYSTEM TELEMETRY HUD", font=("Courier", 16, "bold"), fg="#00ff00", bg="black")
        self.title_label.pack(pady=10)

        self.console_text = tk.Text(root, font=("Consolas", 10), fg="#00ff00", bg="black", bd=0, highlightthickness=0)
        self.console_text.pack(expand=True, fill='both', padx=20, pady=10)
        
        self.log_to_hud("Initializing Command Center...")
        self.log_to_hud("Waiting for Tracer.exe...")
        self.log_to_hud("Right-click your desktop and hit 'Refresh'.\nPress 'ESC' on this window to close.")
        
        self.root.bind("<Escape>", self.close_app)
        self.running = True
        
        # "Prime" the CPU monitor so the first reading isn't 0.0
        psutil.cpu_percent(percpu=True)
        
        # 3. Start Background Threads
        self.start_tracer_thread()
        self.start_telemetry_thread()

    def log_to_hud(self, message):
        """Pushes text to the HUD GUI safely."""
        self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END) # Auto-scroll

    def start_tracer_thread(self):
        """Runs the C++ executable in the background."""
        def run_tracer():
            try:
                process = subprocess.Popen(['tracer.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                for line in process.stdout:
                    if not self.running:
                        break
                    clean_line = line.strip()
                    if clean_line:
                        self.root.after(0, self.log_to_hud, clean_line)
            except FileNotFoundError:
                self.root.after(0, self.log_to_hud, "[ERROR] tracer.exe not found! Please compile the C++ script first.")

        threading.Thread(target=run_tracer, daemon=True).start()

    def get_desktop_files(self):
        """The File Snooper: Grabs the exact payload Explorer has to process."""
        # Windows often hijacks the visual desktop into OneDrive. Let's check both!
        onedrive_desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
        local_desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        
        # Prioritize the OneDrive desktop if it exists
        desktop_path = onedrive_desktop if os.path.exists(onedrive_desktop) else local_desktop
        
        try:
            files = os.listdir(desktop_path)
            # Filter out hidden system files like desktop.ini to keep it clean
            clean_files = [f for f in files if f.lower() != 'desktop.ini']
            return clean_files[:5] + (["...and more"] if len(clean_files) > 5 else [])
        except:
            return ["Unable to read desktop files."]

    def start_telemetry_thread(self):
        """Waits patiently for the actual 'Refresh' click (I/O Spike)."""
        def monitor_explorer():
            last_io = 0
            while self.running:
                # Find Explorer
                explorer_proc = None
                for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'io_counters']):
                    if proc.info['name'].lower() == 'explorer.exe':
                        explorer_proc = proc
                        break
                
                if explorer_proc:
                    current_io = explorer_proc.info['io_counters'].read_count + explorer_proc.info['io_counters'].write_count
                    
                    # If I/O jumps, the user actually clicked "Refresh"
                    if last_io != 0 and (current_io - last_io) > 10:
                        before_io = last_io
                        before_mem = explorer_proc.info['memory_info'].rss / (1024 * 1024)
                        
                        time.sleep(0.3) # Give CPU time to process the refresh
                        
                        after_io = explorer_proc.io_counters().read_count + explorer_proc.io_counters().write_count
                        after_cpu_cores = psutil.cpu_percent(percpu=True)
                        files_processed = self.get_desktop_files()
                        
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        
                        output = f"\n[{timestamp}] ⚡ REFRESH EXECUTION CAUGHT\n"
                        output += "="*50 + "\n"
                        output += "FILE SYSTEM SNOOPER (Explorer Payload):\n"
                        for f in files_processed:
                            output += f"   |-- Verifying: {f}\n"
                        
                        output += f"\nHARDWARE EXECUTION COST:\n"
                        output += f"   |-- I/O Operations Spiked: +{after_io - before_io}\n"
                        output += f"   |-- Explorer RAM Held: {before_mem:.2f} MB\n"
                        output += f"   |-- CPU Core Loads: {after_cpu_cores}\n"
                        output += "="*50 + "\n"
                        
                        self.root.after(0, self.log_to_hud, output)
                        
                        # Reset baseline
                        last_io = explorer_proc.io_counters().read_count + explorer_proc.io_counters().write_count
                        continue
                    
                    last_io = current_io
                
                time.sleep(0.1)

        threading.Thread(target=monitor_explorer, daemon=True).start()

    def close_app(self, event=None):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GodViewHUD(root)
    root.mainloop()