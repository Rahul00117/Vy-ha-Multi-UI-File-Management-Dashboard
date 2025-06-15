import os
import shutil
import pandas as pd
import gradio as gr
from pathlib import Path
import mimetypes
import magic
import webbrowser
import pyperclip

def get_human_readable_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0 or unit == 'GB':
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"

def list_files_df(directory):
    if not os.path.exists(directory):
        directory = os.getcwd()
    files = os.listdir(directory)
    data = []
    for name in files:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            size_str = get_human_readable_size(size)
            data.append([name, "📄 File", size_str])
        else:
            data.append([name, "📁 Folder", "-"])
    df = pd.DataFrame(data, columns=["Name", "Type", "Size"])
    return df

def rename_file(directory, old_name, new_name):
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    os.rename(old_path, new_path)
    return "Rename Successfully"

def delete_path(directory, name):
    path = os.path.join(directory, name)
    if os.path.isfile(path):
        os.remove(path)
        return "File deleted successfully"
    elif os.path.isdir(path):
        shutil.rmtree(path)
        return "Directory deleted successfully"
    else:
        return "Enter correct path"

def create_dir(directory, folder_name):
    path = os.path.join(directory, folder_name)
    os.makedirs(path, exist_ok=True)
    return "Directory Created successfully"

def get_breadcrumbs(path):
    parts = Path(path).parts
    breadcrumbs = []
    for i in range(1, len(parts) + 1):
        breadcrumbs.append("/".join(parts[:i]))
    return breadcrumbs

def update_ui(current_dir, lang="English"):
    df = list_files_df(current_dir)
    breadcrumbs = get_breadcrumbs(current_dir)
    breadcrumb_links = "\n".join([f"<a href='#' onclick='window.location.href=\"/?path={crumb}\"'>{crumb}</a>" for crumb in breadcrumbs])
    return df, breadcrumb_links

def handle_upload(directory, file):
    if file is not None:
        file_path = os.path.join(directory, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        return f"File '{file.name}' uploaded successfully!"
    return "No file selected."

def handle_download(directory, filename):
    if filename:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return file_bytes, filename
    return None, None

def get_file_type(filepath):
    mime = magic.Magic(mime=True)
    return mime.from_file(filepath)

def preview_file(current_dir, filename):
    if filename:
        filepath = os.path.join(current_dir, filename)
        if os.path.isfile(filepath):
            mime = get_file_type(filepath)
            if mime.startswith('image'):
                return gr.Image(value=filepath, label="Image Preview")
            elif mime.startswith('text'):
                with open(filepath, 'r') as f:
                    content = f.read()
                return gr.Textbox(value=content, label="Text Preview", lines=20)
            elif mime == 'application/pdf':
                return gr.HTML(f"<iframe src='{filepath}' width='100%' height='600px'></iframe>")
            else:
                return gr.Textbox(value="Preview not available for this file type.", label="Preview")
    return gr.Textbox(value="Select a file to preview.", label="Preview")

def copy_path(current_dir, filename):
    if filename:
        filepath = os.path.join(current_dir, filename)
        pyperclip.copy(filepath)
        return "Path copied to clipboard!"
    return "No file selected."

def open_in_explorer(current_dir):
    if os.name == 'nt':
        os.startfile(current_dir)
    elif os.name == 'posix':
        os.system(f'xdg-open "{current_dir}"')
    return f"Opened {current_dir} in file explorer."

with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("""
    <h1 style="text-align: center; color: #4a90e2; font-family: sans-serif; font-weight: bold;">
        Vyuh: Ultimate File Management Dashboard
    </h1>
    """)

    with gr.Row():
        current_dir = gr.Textbox(label="Directory Path", value=os.getcwd())
        lang = gr.Radio(["English", "हिंदी"], label="Language", value="English")
        open_explorer_btn = gr.Button("Open in Explorer")

    with gr.Tabs():
        # Tab 1: List Files
        with gr.Tab("List Files"):
            df = gr.DataFrame(label="Files and Folders", value=list_files_df(os.getcwd()))
            breadcrumbs = gr.HTML(label="Current Path", value="")
            current_dir.change(
                lambda dir: update_ui(dir),
                inputs=current_dir,
                outputs=[df, breadcrumbs]
            )
            selected_file = gr.Dropdown(label="Select File/Folder", choices=[], value=None)
            current_dir.change(
                lambda dir: gr.Dropdown(choices=os.listdir(dir), value=None),
                inputs=current_dir,
                outputs=selected_file
            )
            preview = gr.Textbox(label="Preview", value="Select a file to preview.")
            selected_file.change(
                lambda dir, fname: preview_file(dir, fname),
                inputs=[current_dir, selected_file],
                outputs=preview
            )
            copy_btn = gr.Button("Copy Path")
            copy_output = gr.Textbox(label="Copy Status", value="")
            copy_btn.click(
                lambda dir, fname: copy_path(dir, fname),
                inputs=[current_dir, selected_file],
                outputs=copy_output
            )

        # Tab 2: Rename File
        with gr.Tab("Rename File"):
            old_name = gr.Textbox(label="Old Name")
            new_name = gr.Textbox(label="New Name")
            rename_btn = gr.Button("Rename")
            rename_output = gr.Textbox(label="Output")
            rename_btn.click(
                lambda dir, old, new: rename_file(dir, old, new),
                inputs=[current_dir, old_name, new_name],
                outputs=rename_output
            )

        # Tab 3: Delete File/Directory
        with gr.Tab("Delete File/Directory"):
            delete_name = gr.Textbox(label="Name to Delete")
            delete_btn = gr.Button("Delete")
            delete_output = gr.Textbox(label="Output")
            delete_btn.click(
                lambda dir, name: delete_path(dir, name),
                inputs=[current_dir, delete_name],
                outputs=delete_output
            )

        # Tab 4: Create Directory
        with gr.Tab("Create Directory"):
            folder_name = gr.Textbox(label="New Folder Name")
            create_btn = gr.Button("Create")
            create_output = gr.Textbox(label="Output")
            create_btn.click(
                lambda dir, name: create_dir(dir, name),
                inputs=[current_dir, folder_name],
                outputs=create_output
            )

        # Tab 5: Upload File
        with gr.Tab("Upload File"):
            upload_file = gr.File(label="Upload File")
            upload_btn = gr.Button("Upload")
            upload_output = gr.Textbox(label="Output")
            upload_btn.click(
                lambda dir, file: handle_upload(dir, file),
                inputs=[current_dir, upload_file],
                outputs=upload_output
            )

        # Tab 6: Download File
        with gr.Tab("Download File"):
            download_file = gr.Dropdown(label="File to Download", choices=[], value=None)
            download_btn = gr.DownloadButton(label="Download", visible=False)
            current_dir.change(
                lambda dir: gr.Dropdown(choices=[f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))], value=None),
                inputs=current_dir,
                outputs=download_file
            )
            def on_download_click(dir, filename):
                file_bytes, filename = handle_download(dir, filename)
                if file_bytes:
                    return gr.DownloadButton(label="Download", visible=True, value=file_bytes, data=filename)
                else:
                    return gr.DownloadButton(visible=False)
            download_file.change(
                lambda dir, filename: on_download_click(dir, filename),
                inputs=[current_dir, download_file],
                outputs=download_btn
            )

        # Tab 7: File Info
        with gr.Tab("File Info"):
            info_file = gr.Dropdown(label="Select File", choices=[], value=None)
            current_dir.change(
                lambda dir: gr.Dropdown(choices=[f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))], value=None),
                inputs=current_dir,
                outputs=info_file
            )
            info_output = gr.Textbox(label="File Info", value="Select a file to view info.")
            def get_file_info(dir, filename):
                if filename:
                    filepath = os.path.join(dir, filename)
                    if os.path.isfile(filepath):
                        size = os.path.getsize(filepath)
                        size_str = get_human_readable_size(size)
                        mime = get_file_type(filepath)
                        return f"Name: {filename}\nType: {mime}\nSize: {size_str}"
                return "Select a file to view info."
            info_file.change(
                lambda dir, fname: get_file_info(dir, fname),
                inputs=[current_dir, info_file],
                outputs=info_output
            )

    open_explorer_btn.click(
        lambda dir: open_in_explorer(dir),
        inputs=current_dir,
        outputs=gr.Textbox(value="", visible=False)
    )

demo.launch()
