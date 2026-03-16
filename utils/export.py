import os

from tkinter import filedialog, messagebox


def default_output_dir(app):
    return app.folder_path.get().strip() or os.getcwd()


def ask_save_file(app, title, defaultextension, filetypes, initialfile):
    return filedialog.asksaveasfilename(
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes,
        initialdir=default_output_dir(app),
        initialfile=initialfile,
    )


def run_export_with_feedback(export_callable, failure_message, success_message, on_success=None):
    try:
        export_callable()
    except Exception as exc:
        messagebox.showerror("Error", f"{failure_message}: {exc}")
        return False

    if on_success is not None:
        on_success()
    messagebox.showinfo("Success", success_message)
    return True


def resolve_output_folder(app):
    folder = app.folder_path.get()
    if folder:
        return folder

    folder = filedialog.askdirectory(title="Select Folder")
    if not folder:
        return None
    return folder


def next_available_png_path(folder, base_name):
    file_path = os.path.join(folder, f"{base_name}.png")
    if not os.path.exists(file_path):
        return file_path

    suffix = 1
    while True:
        candidate = os.path.join(folder, f"{base_name}_{suffix}.png")
        if not os.path.exists(candidate):
            return candidate
        suffix += 1
