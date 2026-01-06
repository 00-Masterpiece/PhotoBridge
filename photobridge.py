import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from PIL import Image
import pillow_heif

# Enable HEIC support
pillow_heif.register_heif_opener()

SUPPORTED_OUTPUTS = ["jpg", "jpeg", "png", "heic", "webp", "bmp", "tiff"]

cancel_requested = False


def count_images(folder):
    total = 0
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, f)):
            total += 1
    return total


def convert_images(folder, output_ext, log, progress):
    global cancel_requested
    cancel_requested = False

    converted_dir = os.path.join(folder, "Converted Images")
    os.makedirs(converted_dir, exist_ok=True)

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    total = len(files)

    progress["maximum"] = total
    progress["value"] = 0

    for index, filename in enumerate(files, start=1):
        if cancel_requested:
            log.insert(tk.END, "\nConversion cancelled by user.\n")
            return

        input_path = os.path.join(folder, filename)
        name, ext = os.path.splitext(filename)

        try:
            log.insert(tk.END, f"Processing: {filename}\n")
            log.see(tk.END)

            with Image.open(input_path) as img:
                if output_ext.lower() in ["jpg", "jpeg"]:
                    img = img.convert("RGB")

                output_file = f"{name}.{output_ext}"
                output_path = os.path.join(converted_dir, output_file)

                img.save(output_path)

            log.insert(tk.END, f"✔ Converted → {output_file}\n\n")
        except Exception as e:
            log.insert(tk.END, f"✖ Error converting {filename}: {e}\n\n")

        progress["value"] = index
        log.update_idletasks()
        progress.update_idletasks()

    log.insert(tk.END, "🎉 Conversion complete!\n")
    messagebox.showinfo("Done", "All images have been converted successfully.")
    os.startfile(converted_dir)


def start_conversion():
    folder = folder_path.get()
    ext = output_format.get()

    if not folder:
        messagebox.showerror("Error", "Please select a folder.")
        return

    thread = threading.Thread(
        target=convert_images,
        args=(folder, ext, log_box, progress_bar),
        daemon=True
    )
    thread.start()


def cancel_conversion():
    global cancel_requested
    cancel_requested = True


def browse_folder():
    path = filedialog.askdirectory()
    if path:
        folder_path.set(path)
        log_box.delete("1.0", tk.END)


# ---------- GUI ----------

root = tk.Tk()
root.title("PhotoBridge")
root.geometry("700x500")
root.resizable(False, False)

tk.Label(root, text="Step 1: Choose a folder with photos", font=("Segoe UI", 11)).pack(pady=5)

frame1 = tk.Frame(root)
frame1.pack()

folder_path = tk.StringVar()
tk.Entry(frame1, textvariable=folder_path, width=55).pack(side=tk.LEFT, padx=5)
tk.Button(frame1, text="Browse", command=browse_folder, width=10).pack(side=tk.LEFT)

tk.Label(root, text="Step 2: Choose output format", font=("Segoe UI", 11)).pack(pady=10)

output_format = tk.StringVar(value="jpg")
ttk.Combobox(
    root,
    textvariable=output_format,
    values=SUPPORTED_OUTPUTS,
    state="readonly",
    width=15
).pack()

tk.Button(
    root,
    text="Start Conversion",
    command=start_conversion,
    bg="#4CAF50",
    fg="white",
    height=2,
    width=25
).pack(pady=10)

tk.Button(
    root,
    text="Cancel",
    command=cancel_conversion,
    bg="#D9534F",
    fg="white",
    width=10
).pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=650, mode="determinate")
progress_bar.pack(pady=10)

log_box = scrolledtext.ScrolledText(root, height=14, wrap=tk.WORD)
log_box.pack(padx=10, fill=tk.BOTH, expand=True)

root.mainloop()
