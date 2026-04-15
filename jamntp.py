import socket
import time
import datetime
import threading
import tkinter as tk
from tkinter import ttk

# Variabel Global
broadcast_running = False
sock = None

def start_broadcast():
    global broadcast_running, sock

    # Mengambil input IP dan Port dari GUI
    ip = ip_entry.get()
    try:
        port = int(port_entry.get())
    except ValueError:
        log("Error: Port harus berupa angka!")
        return

    try:
        # Inisialisasi Socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Mengaktifkan mode Broadcast agar bisa mengirim ke 255.255.255.255
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        broadcast_running = True
        update_status(True)
        log(f"Offline Broadcast dimulai pada {ip}:{port}")

        def broadcast_loop():
            while broadcast_running:
                # Mengambil waktu dari JAM SISTEM KOMPUTER (Offline)
                waktu_sekarang = datetime.datetime.now().strftime("%H:%M:%S")
                try:
                    # Mengirim data string waktu
                    sock.sendto(waktu_sekarang.encode(), (ip, port))
                    
                    # Update tampilan GUI
                    root.after(0, lambda: update_label(waktu_sekarang))
                    root.after(0, lambda: log(f"Sent (Offline): {waktu_sekarang}"))
                except Exception as e:
                    root.after(0, lambda: log(f"Error: {e}"))
                    stop_broadcast()
                    break
                
                # Jeda 1 detik agar seperti jam dinding
                time.sleep(1)

        # Menjalankan loop di thread berbeda agar GUI tidak hang/macet
        threading.Thread(target=broadcast_loop, daemon=True).start()
        
    except Exception as e:
        log(f"Gagal memulai socket: {e}")

def stop_broadcast():
    global broadcast_running, sock
    broadcast_running = False
    if sock:
        sock.close()
    update_status(False)
    log("Broadcast dihentikan.")

def update_label(waktu):
    time_label.config(text=waktu)

def update_status(status):
    if status:
        status_label.config(text="STATUS: BROADCAST AKTIF ✅", foreground="green")
        start_btn.config(state="disabled")
        stop_btn.config(state="normal")
    else:
        status_label.config(text="STATUS: OFFLINE / MATI ❌", foreground="red")
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

def on_close():
    stop_broadcast()
    root.destroy()

# === UI TKINTER ===
root = tk.Tk()
root.title("Python Offline Time Server")
root.geometry("450x450")
root.protocol("WM_DELETE_WINDOW", on_close)

# Header
ttk.Label(root, text="LOCAL TIME BROADCASTER", font=("Arial", 14, "bold")).pack(pady=10)
ttk.Label(root, text="Tanpa Internet (Direct UDP)").pack()

# Input Frame
frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Broadcast IP:").grid(row=0, column=0, sticky="w")
ip_entry = ttk.Entry(frame)
ip_entry.insert(0, "255.255.255.255") # IP Universal untuk Offline
ip_entry.grid(row=0, column=1, padx=5, pady=2)

ttk.Label(frame, text="UDP Port:").grid(row=1, column=0, sticky="w")
port_entry = ttk.Entry(frame)
port_entry.insert(0, "8888")
port_entry.grid(row=1, column=1, padx=5, pady=2)

# Control Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=5)
start_btn = ttk.Button(btn_frame, text="Mulai", command=start_broadcast)
start_btn.grid(row=0, column=0, padx=5)
stop_btn = ttk.Button(btn_frame, text="Berhenti", command=stop_broadcast, state="disabled")
stop_btn.grid(row=0, column=1, padx=5)

# Indikator
status_label = ttk.Label(root, text="STATUS: OFFLINE / MATI ❌", font=("Arial", 10, "bold"), foreground="red")
status_label.pack(pady=10)

# Jam Besar
time_label = ttk.Label(root, text="00:00:00", font=("Consolas", 40, "bold"))
time_label.pack(pady=10)

# Log
log_box = tk.Text(root, height=8, width=50, font=("Consolas", 9))
log_box.pack(pady=5, padx=10)

# Jalankan otomatis saat buka aplikasi
root.after(1000, start_broadcast)

root.mainloop()