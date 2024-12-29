import os
import shutil
from tuf_client import init_tofu, download

# Configuration for TUF
METADATA_DIR = "metadata"  # Local directory for TUF metadata
DOWNLOAD_DIR = "downloads"  # Directory to store downloaded files

BASE_URL = "https://tuf-server-y43f.onrender.com"
APP_NAME = "color_changer.exe"  # Name of the .exe to be updated
target = f"targets/{APP_NAME}"

def initialize_updater(base_url):
    """
    Initialize the TUF Updater for version 5.1.0.
    """
    init_tofu(base_url=base_url)


def download_update(base_url, target):
    """
    Download and verify the update using TUF.
    """
    download_up = download(base_url=base_url, target=target)
    if download_up:
        download_path = os.path.join(DOWNLOAD_DIR, "targets%2f" + APP_NAME)
        return download_path


def replace_executable(new_exe_path):
    """
    Replace the running executable with the updated version.
    """
    current_exe = os.path.join(os.getcwd(), APP_NAME)  # Path to the current color_changer.exe
    backup_exe = current_exe + ".bak"

    try:
        # Backup the current executable
        if os.path.exists(backup_exe):
            os.remove(backup_exe)
        shutil.move(current_exe, backup_exe)

        # Replace the current executable with the new version
        shutil.copy2(new_exe_path, current_exe)
        print("Executable updated successfully.")
    except Exception as e:
        print("Failed to replace the executable.")
        print(e)


if __name__ == "__main__":
    updater = initialize_updater(BASE_URL)
    new_exe_path = download_update(BASE_URL, target)
    if new_exe_path:
        replace_executable(new_exe_path)
