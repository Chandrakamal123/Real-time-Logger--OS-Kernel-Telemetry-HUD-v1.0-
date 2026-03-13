#include <windows.h>
#include <iostream>
#include <string>

// Global hook handle
HHOOK hMouseHook;

void TraceAnySignal(MSLLHOOKSTRUCT* mouseStruct) {
    // 1. Identify the Window handle at the exact mouse coordinates
    HWND hWnd = WindowFromPoint(mouseStruct->pt);
    
    if (hWnd != NULL) {
        DWORD processID;
        // 2. Extract the Process ID and the specific Thread ID
        DWORD threadID = GetWindowThreadProcessId(hWnd, &processID);

        // 3. Get the Class Name (The 'DNA' of the window)
        char className[256];
        GetClassNameA(hWnd, className, sizeof(className));

        // 4. Get the Window Title (What you see in the taskbar)
        char windowTitle[256];
        GetWindowTextA(hWnd, windowTitle, sizeof(windowTitle));

        // 5. Pipe the raw telemetry to Python in a parseable format
        std::cout << "SIGNAL_INTERCEPTED|" 
                  << mouseStruct->pt.x << "|" 
                  << mouseStruct->pt.y << "|" 
                  << className << "|" 
                  << (strlen(windowTitle) > 0 ? windowTitle : "Unnamed Window") << "|" 
                  << processID << "|" 
                  << threadID << std::endl;
    }
}

LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    // We now watch for LEFT or RIGHT clicks anywhere on the OS
    if (nCode == HC_ACTION && (wParam == WM_LBUTTONDOWN || wParam == WM_RBUTTONDOWN)) {
        MSLLHOOKSTRUCT* mouseStruct = (MSLLHOOKSTRUCT*)lParam;
        TraceAnySignal(mouseStruct);
    }
    return CallNextHookEx(hMouseHook, nCode, wParam, lParam);
}

int main() {
    std::cout << std::unitbuf; // Disable buffering for instant HUD updates
    
    // Install the Global Hook
    hMouseHook = SetWindowsHookEx(WH_MOUSE_LL, MouseProc, NULL, 0);
    
    if (hMouseHook == NULL) {
        std::cerr << "CRITICAL: Kernel Hook Failed. (Try running as Admin)" << std::endl;
        return 1;
    }

    std::cout << "MARAUDER CORE ACTIVE: Monitoring all System Signals..." << std::endl;

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    UnhookWindowsHookEx(hMouseHook);
    return 0;
}