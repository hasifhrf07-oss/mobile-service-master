"""
Mobile Service Master — Client Launcher
Opens cloud dashboard in browser + checks version
"""
import os
import sys
import time
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox

# Configuration
CLOUD_URL = "https://mobile-service-master.onrender.com"
VERSION = "3.1.0"


class ClientLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mobile Service Master")
        self.root.geometry("480x360")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#89b4fa", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔧 Mobile Service Master",
            font=("Segoe UI", 16, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e"
        ).pack(pady=(18, 4))

        tk.Label(
            header,
            text="Client Access",
            font=("Segoe UI", 11),
            bg="#89b4fa",
            fg="#1e1e2e"
        ).pack()

        # Body
        body = tk.Frame(self.root, bg="#1e1e2e")
        body.pack(fill="both", expand=True, padx=30, pady=30)

        tk.Label(
            body,
            text="আপনার ডিভাইস connect করতে\nনিচের button-এ click করুন",
            font=("Nirmala UI", 11),
            bg="#1e1e2e",
            fg="#cdd6f4",
            justify="center"
        ).pack(pady=(0, 20))

        # Open button
        self.btn = tk.Button(
            body,
            text="🌐  Open Dashboard",
            font=("Segoe UI", 13, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#b4befe",
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=14,
            command=self.open_dashboard
        )
        self.btn.pack(fill="x")

        # Status
        self.status = tk.Label(
            body,
            text="✓ Connected to cloud",
            font=("Segoe UI", 10),
            bg="#1e1e2e",
            fg="#a6e3a1"
        )
        self.status.pack(pady=(15, 0))

        # Footer
        tk.Label(
            body,
            text=f"v{VERSION}  •  {CLOUD_URL}",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#6c7086"
        ).pack(side="bottom")

    def open_dashboard(self):
        try:
            webbrowser.open(CLOUD_URL + "/dashboard-v2")
            self.status.config(text="✓ Browser opened", fg="#a6e3a1")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser:\n{e}")
            self.status.config(text=f"✗ {e}", fg="#f38ba8")

    def run(self):
        self.root.mainloop()


def main():
    print()
    print("=" * 62)
    print("   Mobile Service Master — CLIENT")
    print("=" * 62)
    print(f"   Cloud URL: {CLOUD_URL}")
    print(f"   Version:   {VERSION}")
    print()
    print("   Opening window...")
    print("=" * 62)
    print()

    try:
        app = ClientLauncher()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
