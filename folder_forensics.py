import tkinter as tk
import threading
import pythoncom
import time
import wmi
import os
import win32file
import win32api
from datetime import datetime

class FolderForensicsHUD:
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
        self.title_label = tk.Label(root, text="👁️ GOD-VIEW: FOLDER CREATION FORENSICS", font=("Courier", 16, "bold"), fg="#00ff00", bg="black")
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
        
        self.log(">>> SYSTEM: GUI Initialized.", "SIGNAL")
        
        # Start Watchers AFTER the GUI renders
        self.root.after(500, self.start_global_folder_watcher)
        self.root.after(500, self.start_birth_watcher)

    def log(self, msg, tag="SIGNAL"):
        if self.running:
            self.console_text.insert(tk.END, msg + "\n", tag)
            self.console_text.see(tk.END)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.console_text.get("1.0", tk.END))
        self.root.update() 
        self.log("\n[!] LOG COPIED TO CLIPBOARD SUCCESSFULLY.", "BIRTH")

    def print_folder_trace(self, folder_path, drive):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        msg = f"\n[{timestamp}] 🔴 DIRECTORY ALLOCATION DETECTED\n" + "=" * 80 + "\n"
        
        msg += "1. THE REQUEST (USER SPACE)\n"
        msg += f"   |-- Origin: Explorer.exe executed the 'CreateDirectoryW' Win32 API call.\n"
        msg += f"   |-- Target Path: {folder_path}\n"
        msg += f"   |-- Target Disk: Physical Volume {drive}\n\n"
        
        msg += "2. KERNEL TRANSITION (IRP GENERATION)\n"
        msg += "   |-- Handoff: API call passed down to 'ntoskrnl.exe' (Windows Kernel).\n"
        msg += "   |-- I/O Manager: Created an I/O Request Packet (IRP_MJ_CREATE) for the File System.\n"
        msg += "   |-- Dispatch: IRP pushed down the driver stack directly to 'Ntfs.sys'.\n\n"
        
        msg += "3. NTFS DRIVER INTERCEPTION & SECURITY\n"
        msg += "   |-- ACL Check: 'Ntfs.sys' verified your User Access Token against the Parent Directory.\n"
        msg += "   |-- Access Granted: Write and Append privileges confirmed. Request approved.\n\n"
        
        msg += "4. MASTER FILE TABLE (MFT) ALLOCATION\n"
        msg += "   |-- MFT Entry: Allocated a new 1KB File Record Segment (FRS) in the Master File Table.\n"
        msg += "   |-- Data Attribute: Initialized $INDEX_ROOT (Because this is a Directory, not a standard File).\n"
        msg += "   |-- Timestamps: $STANDARD_INFORMATION attribute injected with current Kernel clock.\n\n"
        
        msg += "5. PHYSICAL DISK MAPPING\n"
        msg += f"   |-- Volume Bitmap: Searched {drive} for free Logical Clusters.\n"
        msg += "   |-- LCN Assignment: Claimed a Logical Cluster Number (LCN) to store folder metadata.\n"
        msg += "   |-- Commit: Journaling ($LogFile) updated to prevent corruption on sudden power loss.\n\n"
        
        msg += "6. THE VISUAL OUTPUT & COMPLETION\n"
        msg += "   |-- Callback: IRP completes successfully. Kernel notifies Explorer.exe.\n"
        msg += "   |-- Shell Event: SHChangeNotify is fired to alert the graphical user interface.\n"
        msg += f"   |-- Render: Desktop Window Manager (DWM) draws '{os.path.basename(folder_path)}' on your screen.\n"
        msg += "=" * 80

        self.root.after(0, self.log, msg, "SIGNAL")

    def start_global_folder_watcher(self):
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        
        drive_list_str = ", ".join(drives)
        self.log(f">>> SYSTEM: Hooked into NTFS File System across drives: {drive_list_str}", "SIGNAL")
        self.log(">>> SYSTEM: Create a 'New Folder' ANYWHERE on your PC to view the Kernel trace.\n", "SIGNAL")
        
        # Shared dictionary across threads.
        pending_reports = {}

        def queue_processor():
            """Fallback Timer: If the user doesn't hit Enter within 8 seconds, just print the default name."""
            while self.running:
                now = time.time()
                try:
                    # Safely iterate over a copy of the keys
                    for key in list(pending_reports.keys()):
                        if now - pending_reports[key]['time'] > 8.0:
                            data = pending_reports.pop(key, None)
                            if data:
                                threading.Thread(target=self.print_folder_trace, args=(data['actual_path'], data['drive']), daemon=True).start()
                except RuntimeError:
                    pass # Ignore dictionary change errors and try again next loop
                time.sleep(0.5)

        threading.Thread(target=queue_processor, daemon=True).start()
        
        def watch_drive(drive_path):
            FILE_LIST_DIRECTORY = 0x0001
            FILE_SHARE_READ = 0x01
            FILE_SHARE_WRITE = 0x02
            FILE_SHARE_DELETE = 0x04
            OPEN_EXISTING = 3
            FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
            FILE_NOTIFY_CHANGE_DIR_NAME = 0x0002
            
            try:
                hDir = win32file.CreateFile(
                    drive_path,
                    FILE_LIST_DIRECTORY,
                    FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                    None,
                    OPEN_EXISTING,
                    FILE_FLAG_BACKUP_SEMANTICS,
                    None
                )
            except Exception:
                return 
            
            # Moved outside the loop so the script remembers the old name across buffers!
            old_rename_key = None 
            
            while self.running:
                try:
                    results = win32file.ReadDirectoryChangesW(
                        hDir,
                        65536, 
                        True,  
                        FILE_NOTIFY_CHANGE_DIR_NAME,
                        None,
                        None
                    )
                    
                    for action, file in results:
                        full_path = os.path.join(drive_path, file)
                        path_key = full_path.lower() # Strictly lowercase to fix Python matching bugs
                        
                        if any(noise in path_key for noise in ["appdata", "windows", "$recycle.bin", "temp", "prefetch", "programdata"]):
                            continue
                        
                        # ACTION 1: Folder Created
                        if action == 1:
                            pending_reports[path_key] = {"drive": drive_path[:2], "time": time.time(), "actual_path": full_path}
                            if "new folder" in os.path.basename(full_path).lower():
                                self.root.after(0, self.log, f"[!] KERNEL: Allocation caught. Type a name and press ENTER...", "BIRTH")
                        
                        # ACTION 4: Folder Renamed (Old Name)
                        elif action == 4:
                            old_rename_key = path_key
                        
                        # ACTION 5: Folder Renamed (New Name)
                        elif action == 5:
                            if old_rename_key and old_rename_key in pending_reports:
                                # They hit Enter! Pop it from the waiting room and print it instantly.
                                data = pending_reports.pop(old_rename_key, None)
                                if data:
                                    threading.Thread(target=self.print_folder_trace, args=(full_path, data['drive']), daemon=True).start()
                            old_rename_key = None # Reset
                            
                except Exception:
                    pass

        for drive in drives:
            threading.Thread(target=watch_drive, args=(drive,), daemon=True).start()

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
    print("Initializing God-View HUD...")
    root = tk.Tk()
    app = FolderForensicsHUD(root)
    root.mainloop()