import time
import psutil
import os
from datetime import datetime

def get_explorer_stats():
    """Captures granular CPU, Memory, and IO usage of the Explorer process."""
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'io_counters']):
        if proc.info['name'].lower() == 'explorer.exe':
            return proc, proc.info
    return None, None

def print_god_view_trace(proc, before_io, before_mem, before_cpu_cores):
    """Simulates the hardware-level trace with live data."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    # Give the CPU a fraction of a second to process the refresh so we can capture the "After" state
    time.sleep(0.2) 
    
    after_io = proc.io_counters().read_count + proc.io_counters().write_count
    after_mem = proc.memory_info().rss / (1024 * 1024)
    after_cpu_cores = psutil.cpu_percent(percpu=True)
    
    print(f"\n[{timestamp}] 🔴 REFRESH SIGNAL DETECTED")
    print("=" * 60)
    
    time.sleep(0.3)
    print("1. THE TRIGGER & SIGNAL ROUTING")
    print("   |-- Origin: Mouse hardware sent a USB Interrupt Request (IRQ) to the Motherboard.")
    print("   |-- CPU Action: CPU paused current tasks (Context Switch) to read the mouse click.")
    print("   |-- Kernel Handoff: Windows Kernel (ntoskrnl.exe) translated the physical click into a virtual screen coordinate.")
    print("   |-- Signal Owner: The signal was handed to User Space -> process 'Explorer.exe'.")
    
    time.sleep(0.4)
    print("\n2. TRANSLATION TO MACHINE LANGUAGE")
    print("   |-- Note: Windows is pre-compiled. No on-the-fly compiling happens here.")
    print("   |-- Fetching: Explorer.exe calls the Win32 API (User32.dll).")
    print("   |-- Machine Code: API commands are broken down into x86-64 Assembly instructions (e.g., MOV, CMP, JMP).")
    print("   |-- Transport: The Memory Controller moves these instructions from your RAM to the CPU's L1 Instruction Cache.")
    
    time.sleep(0.4)
    print("\n3. SYSTEM STATE: BEFORE REFRESH")
    print(f"   |-- Explorer IO Operations: {before_io:,}")
    print(f"   |-- Explorer RAM Allocated: {before_mem:.2f} MB")
    print(f"   |-- CPU Core Loads: {before_cpu_cores}")
    
    time.sleep(0.4)
    print("\n4. CPU EXECUTION (THE APPROVAL)")
    print("   |-- Execution: The CPU's Arithmetic Logic Unit (ALU) executes the instructions.")
    print("   |-- Action 1: Query the Master File Table (NTFS) to see if Desktop files changed.")
    print("   |-- Action 2: Recalculate the X and Y grid coordinates for every desktop icon.")
    print("   |-- Approval: CPU finishes math, flags the Desktop Window Manager (DWM.exe) to repaint.")
    
    time.sleep(0.4)
    print("\n5. SYSTEM STATE: AFTER REFRESH")
    print(f"   |-- Explorer IO Operations: {after_io:,} (+{after_io - before_io} operations)")
    print(f"   |-- Explorer RAM Allocated: {after_mem:.2f} MB")
    print(f"   |-- CPU Core Loads: {after_cpu_cores}")
    
    time.sleep(0.4)
    print("\n6. THE VISUAL OUTPUT")
    print("   |-- Render: DWM sends the new pixel map to your GPU Framebuffer.")
    print("   |-- Display: Your monitor refreshes its pixels (e.g., at 60Hz or 144Hz).")
    print("   |-- Result: The screen flickers. The refresh is complete.")
    print("=" * 60 + "\n")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- 👁️  GOD-VIEW WINDOWS REFRESH VISUALIZER ---")
    print("Hooked into OS Telemetry. Waiting for Explorer.exe IO spike...")
    print("Right-click your desktop and hit 'Refresh'. Press Ctrl+C to exit.\n")

    last_io = 0
    
    try:
        while True:
            proc, stats = get_explorer_stats()
            if proc and stats:
                current_io = stats['io_counters'].read_count + stats['io_counters'].write_count
                
                # Check for an IO burst indicating a refresh
                if last_io != 0 and (current_io - last_io) > 10:
                    before_io = last_io
                    before_mem = stats['memory_info'].rss / (1024 * 1024)
                    before_cpu_cores = psutil.cpu_percent(percpu=True)
                    
                    # Fire the visualizer trace
                    print_god_view_trace(proc, before_io, before_mem, before_cpu_cores)
                    
                    # Reset last_io to the new baseline to avoid infinite looping
                    last_io = proc.io_counters().read_count + proc.io_counters().write_count
                    continue
                
                last_io = current_io

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[!] God-View Disengaged. Shutting down logger.")

if __name__ == "__main__":
    main()