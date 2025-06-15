import os
import shutil
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="Vyūha (व्यूह) – File Management Dashboard", layout="wide")


# ---------- Helper Functions ----------

def get_human_readable_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0 or unit == 'GB':
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"

def list_files_df(directory):
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

def preview_file(file_path):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            st.image(file_path)
        elif file_path.lower().endswith(('.txt', '.csv', '.md', '.py', '.json', '.xml')):
            with open(file_path, 'r') as f:
                content = f.read()
            st.code(content, language="text")
    except Exception as e:
        st.error(f"Cannot preview file: {e}")

def get_breadcrumbs(path):
    parts = Path(path).parts
    breadcrumbs = []
    for i in range(1, len(parts) + 1):
        breadcrumbs.append(parts[:i])
    return breadcrumbs

# ---------- Language Setup ----------

lang = st.sidebar.radio("Language", ["English", "हिंदी"])
if lang == "हिंदी":
    menu = ["होम", "फ़ाइलें सूची", "फ़ाइल का नाम बदलें", "फ़ाइल/डायरेक्टरी हटाएं", "डायरेक्टरी बनाएं", "फ़ाइल अपलोड करें", "फ़ाइल डाउनलोड करें"]
    dir_label = "डायरेक्टरी पथ दर्ज करें:"
    home_msg = "फ़ाइल प्रबंधन डैशबोर्ड में आपका स्वागत है!"
    use_sidebar = "साइडबार का उपयोग करके फ़ाइलें प्रबंधित करें।"
    list_title = "फ़ाइलें और फोल्डरों की सूची"
    rename_title = "फ़ाइल का नाम बदलें"
    old_name_label = "पुराना फ़ाइल नाम दर्ज करें:"
    new_name_label = "नया फ़ाइल नाम दर्ज करें:"
    delete_title = "फ़ाइल/डायरेक्टरी हटाएं"
    delete_prompt = "हटाने के लिए फ़ाइल/डायरेक्टरी का नाम दर्ज करें:"
    create_title = "डायरेक्टरी बनाएं"
    create_prompt = "नई डायरेक्टरी का नाम दर्ज करें:"
    upload_title = "फ़ाइल अपलोड करें"
    download_title = "फ़ाइल डाउनलोड करें"
    select_file = "डाउनलोड के लिए फ़ाइल चुनें"
    no_files = "डाउनलोड के लिए कोई फ़ाइल उपलब्ध नहीं है।"
    copyright = "© 2025 फ़ाइल प्रबंधन डैशबोर्ड"
else:
    menu = ["Home", "List Files", "Rename File", "Delete File/Directory", "Create Directory", "Upload File", "Download File"]
    dir_label = "Enter directory path:"
    home_msg = "Welcome to the File Management Dashboard!"
    use_sidebar = "Use the sidebar to navigate and manage your files."
    list_title = "List of Files and Folders"
    rename_title = "Rename File"
    old_name_label = "Enter old file name:"
    new_name_label = "Enter new file name:"
    delete_title = "Delete File or Directory"
    delete_prompt = "Enter file or directory name to delete:"
    create_title = "Create Directory"
    create_prompt = "Enter new directory name to create:"
    upload_title = "Upload File"
    download_title = "Download File"
    select_file = "Select file to download"
    no_files = "No files available to download."
    copyright = "© 2025 File Management Dashboard"

# ---------- Main App ----------

def main():
    st.title("Vyūha (व्यूह) – File Management Dashboard")
    st.markdown("---")

    theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("<style>body {background-color: #1e1e1e; color: white;}</style>", unsafe_allow_html=True)

    choice = st.sidebar.selectbox("Menu", menu)
    st.sidebar.markdown("---")

    # Directory Input
    st.sidebar.write("### " + dir_label)
    default_dir = os.getcwd()
    dir_input = st.sidebar.text_input(dir_label, value=default_dir)
    current_dir = dir_input if os.path.exists(dir_input) else default_dir

    # Breadcrumb navigation
    breadcrumbs = get_breadcrumbs(current_dir)
    for i, crumb in enumerate(breadcrumbs):
        crumb_path = os.path.join(*crumb)
        if st.sidebar.button("/".join(crumb), key=f"crumb_{i}"):
            current_dir = crumb_path

    # Go up one directory
    if st.sidebar.button("Go to Parent Directory"):
        parent_dir = os.path.dirname(current_dir)
        if os.path.exists(parent_dir):
            current_dir = parent_dir
            st.sidebar.success(f"Selected Directory: `{current_dir}`")
        else:
            st.sidebar.error("Cannot go to parent directory.")

    # Subfolders
    subfolders = [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f))]
    if subfolders:
        selected_subfolder = st.sidebar.selectbox("Go to Subfolder", [""] + subfolders)
        if selected_subfolder:
            current_dir = os.path.join(current_dir, selected_subfolder)

    # Recent Directories
    if 'recent_dirs' not in st.session_state:
        st.session_state.recent_dirs = []
    if current_dir not in st.session_state.recent_dirs:
        st.session_state.recent_dirs.append(current_dir)
    if len(st.session_state.recent_dirs) > 5:
        st.session_state.recent_dirs.pop(0)
    st.sidebar.write("### Recent Directories")
    for d in st.session_state.recent_dirs:
        if st.sidebar.button(d, key=f"recent_{d}"):
            current_dir = d

    # ----- Menu Logic -----
    if choice == menu[0]:  # Home
        st.write(home_msg)
        st.write(use_sidebar)
        st.write(f"Current Directory: `{current_dir}`")

    elif choice == menu[1]:  # List Files
        st.subheader(list_title)
        df = list_files_df(current_dir)
        search = st.text_input("Search files/folders")
        if search:
            df = df[df['Name'].str.contains(search, case=False)]
        st.dataframe(df, use_container_width=True)
        selected_file = st.selectbox("Select a file/folder to preview", [""] + df['Name'].tolist())
        if selected_file:
            file_path = os.path.join(current_dir, selected_file)
            if os.path.isfile(file_path):
                preview_file(file_path)
            else:
                st.info("Folder selected. Only files can be previewed.")

    elif choice == menu[2]:  # Rename File
        st.subheader(rename_title)
        old_name_val = st.text_input(old_name_label)
        new_name_val = st.text_input(new_name_label)
        if st.button("Rename"):
            if old_name_val and new_name_val:
                result = rename_file(current_dir, old_name_val, new_name_val)
                st.success(result)
            else:
                st.error("Please enter both old and new names.")

    elif choice == menu[3]:  # Delete
        st.subheader(delete_title)
        name = st.text_input(delete_prompt)
        if st.button("Delete"):
            if name:
                result = delete_path(current_dir, name)
                st.success(result)
            else:
                st.error("Please enter a name.")

    elif choice == menu[4]:  # Create Dir
        st.subheader(create_title)
        folder_name = st.text_input(create_prompt)
        if st.button("Create"):
            if folder_name:
                result = create_dir(current_dir, folder_name)
                st.success(result)
            else:
                st.error("Please enter a directory name.")

    elif choice == menu[5]:  # Upload File
        st.subheader(upload_title)
        uploaded_file = st.file_uploader("Choose a file to upload")
        if uploaded_file is not None:
            file_path = os.path.join(current_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    elif choice == menu[6]:  # Download File
        st.subheader(download_title)
        files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]
        if files:
            selected_file = st.selectbox(select_file, files)
            if st.button("Download"):
                file_path = os.path.join(current_dir, selected_file)
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                st.download_button("Download File", data=file_bytes, file_name=selected_file)
        else:
            st.info(no_files)

    st.sidebar.markdown("---")
    st.sidebar.write(copyright)

# Run the app
if __name__ == '__main__':
    main()
