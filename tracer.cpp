#include <windows.h>
#include <iostream>
#include <string>

// Global hook handle
HHOOK hMouseHook;

// Function to find who owns the window under the cursor
void TraceSignalDestination(POINT pt) {
    // 1. Find the physical window handle at the mouse coordinates
    HWND hWnd = WindowFromPoint(pt);
    if (hWnd) {
        // 2. Identify the exact CPU Thread and Process ID that owns this signal
        DWORD processID;
        DWORD threadID = GetWindowThreadProcessId(hWnd, &processID);
        
        char windowTitle[256];
        GetWindowTextA(hWnd, windowTitle, sizeof(windowTitle));
        
        char className[256];
        GetClassNameA(hWnd, className, sizeof(className));

        std::cout << "   |-- Hardware Signal Intercepted at X:" << pt.x << " Y:" << pt.y << "\n";
        std::cout << "   |-- Signal Routing To Window Class: " << className << "\n";
        std::cout << "   |-- Signal Owner (Process ID): " << processID << "\n";
        std::cout << "   |-- Executing on Thread ID: " << threadID << "\n";
        
        // "WorkerW" or "Progman" are the wallpaper, "SysListView32" is the icon grid
        // "WorkerW" or "Progman" are the wallpaper, "SysListView32" is the icon grid
        if (std::string(className) == "WorkerW" || std::string(className) == "Progman" || std::string(className) == "SysListView32") {
            std::cout << "   |-- TARGET CONFIRMED: Desktop Background / Icon Grid (Explorer.exe)\n";
            std::cout << "   |-- Action: The OS Kernel is now pushing this signal into Thread " << threadID << "'s message queue.\n";
            std::cout << "   |-- CPU Handoff: The CPU will now fetch Registry keys to render the 'Right-Click Context Menu'.\n";
        }
    }
}

// The callback function that the Windows Kernel calls when mouse hardware interrupts occur
LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) {
        MSLLHOOKSTRUCT* pMouseStruct = (MSLLHOOKSTRUCT*)lParam;
        
        // We are watching for the exact moment the Right Mouse Button goes UP (the trigger for the context menu)
        if (wParam == WM_RBUTTONUP) {
            std::cout << "\n======================================================\n";
            std::cout << "🔴 RAW HARDWARE INTERRUPT (IRQ) DETECTED\n";
            std::cout << "======================================================\n";
            
            TraceSignalDestination(pMouseStruct->pt);
            
            std::cout << "======================================================\n\n";
        }
    }
    // Pass the signal down the chain so your mouse actually still works
    return CallNextHookEx(hMouseHook, nCode, wParam, lParam);
}

int main() {
    // FORCE NO BUFFERING: This tells C++ to send text to Python instantly
    std::cout << std::unitbuf; 
    
    std::cout << "--- C++ BARE-METAL SIGNAL TRACER ---\n";
    std::cout << "Installing Low-Level Mouse Hook into the Windows Kernel...\n";
    
    // Set up the hardware hook directly into the OS
    hMouseHook = SetWindowsHookEx(WH_MOUSE_LL, MouseProc, NULL, 0);
    
    if (hMouseHook == NULL) {
        std::cerr << "Failed to install hook! Run as Administrator.\n";
        return 1;
    }

    std::cout << "Hook Active. RIGHT-CLICK anywhere on your desktop to trace the signal route.\n";
    std::cout << "Press Ctrl+C to exit.\n\n";

    // A standard Windows message loop to keep the program alive and listening to the Kernel
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    UnhookWindowsHookEx(hMouseHook);
    return 0;
}