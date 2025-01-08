import os
import subprocess
import time
import ctypes

from tuf_client import download

APP_NAME = "color_changer.exe" # Name of the .exe to be updated
BASE_URL = "https://tuf-server-y43f.onrender.com"
target = f"targets/{APP_NAME}"
privileged_path = "privileged_download.exe"

def launch_application():
    """
    Launch the application.
    """
    try:
        print(f"Launching {APP_NAME}...")
        subprocess.Popen([os.path.abspath(APP_NAME)], shell=True)
    except Exception as e:
        print("Failed to launch application.")
        print(e)
        input("Press Enter to exit...")


def check_update(base_url, target, privileged_path) -> bool:
    """
    Download and verify the update using TUF.
    """
    download_up = download(base_url=base_url, target=target)
    if download_up == True:

        # run with admin privileged right
        print("Requesting elevated privileges for the update...")
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", privileged_path, None, None, 1)
        if result <= 32:
            raise RuntimeError(f"Failed to launch updater with elevated privileges. Error code: {result}")

        # Wait for the privileged process to complete
        print("Waiting for the privileged update process to complete...")
        while True:
            # Check if the process is still running
            try:
                # Using the process name to check if it's running
                task_list = subprocess.check_output("tasklist", shell=True).decode()
                if privileged_path not in task_list:
                    break
            except Exception as e:
                raise RuntimeError("Error while monitoring the updater process.") from e

            time.sleep(1)  # Wait a bit before checking again
        return True

    elif download_up == "up_to_date":
        return True
    else:
        return False


if __name__ == "__main__":
    print("Starting update check...")
    try:
        # Run the updater and wait for it to complete
        update = check_update(base_url=BASE_URL, target=target, privileged_path=privileged_path)
        if update:
            # Ensure update completed before launching application
            print("Update check complete. Launching application...")
            time.sleep(2)
            launch_application()

    except subprocess.CalledProcessError as e:
        print(f"Updater failed with return code {e.returncode}.")
        print("Update process aborted.")
        input("Press Enter to exit...")
        exit(1)

    except Exception as e:
        print("Unexpected error during update or application launch.")
        print(e)
        input("Press Enter to exit...")
        exit(1)
