import os
import shutil
import time

# TUF
from tuf.ngclient import Updater

# private
from progress_hook import ProgressWindow
from network_download import CustomFetcher
from tuf_client import build_metadata_dir

BASE_URL = "https://tuf-server-y43f.onrender.com"
APP_NAME = "color_changer.exe"  # Name of the .exe to be updated
target = f"targets/{APP_NAME}"
DOWNLOAD_DIR = "./downloads"
downloaded_path = os.path.join(DOWNLOAD_DIR, "targets%2f" + APP_NAME)  # path which the target is downloaded


def privileged_download(base_url: str, target: str):
    """Run the tuf_clinet download process with admin privileged right with serialised data (updater and info) ."""

    print("Proceeding with the update...")
    metadata_dir = build_metadata_dir(base_url)

    # Initialize updater with a fetcher that does not show progress for metadata
    updater = Updater(
        metadata_dir=metadata_dir,
        metadata_base_url=f"{base_url}/metadata/",
        target_base_url=f"{base_url}/",
        target_dir=DOWNLOAD_DIR,
        fetcher=CustomFetcher(progress_hook=None),  # No progress for metadata refresh
    )

    # Refresh metadata (no progress hook here)
    print("Refreshing metadata...")
    updater.refresh()

    # Get target info
    print(f"Checking target: {target}")
    info = updater.get_targetinfo(target)

    if info is None:
        print(f"Target {target} not found in the repository.")
        return False

    # Check if the target is already cached
    path = updater.find_cached_target(info)
    if path:
        print(f"Target is already available in {path}. No update required.")
        return False

    # Initialize a progress window
    progress_window = ProgressWindow()

    # Define a callback function for progress updates
    def progress_callback(progress):
        progress_window.update(progress)
        if progress_window.complete:
            progress_window.close()

    # Now set the fetcher with the progress hook for downloading the target
    updater._fetcher = CustomFetcher(progress_hook=progress_callback)

    # Download the target and display progress
    path = updater.download_target(info)
    print(f"Target downloaded and available in {path}.")

    return True


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
        print("backing up the current app")
        time.sleep(60)

        # Replace the current executable with the copy of a new version
        print("creating copy of the new app")
        time.sleep(60)
        shutil.copy2(new_exe_path, current_exe)
        print("Executable updated successfully.")
    except Exception as e:
        print("Failed to replace the executable.")
        print(e)


download = privileged_download(base_url=BASE_URL, target=target)

if download:
    replace_executable(new_exe_path=downloaded_path)
else:
    print("An error occurred with downloading update")
