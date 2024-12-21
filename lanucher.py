import os
import subprocess
import time

APP_NAME = "color_changer.exe"
UPDATER_NAME = "updater.exe"


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


if __name__ == "__main__":
    print("Starting update check...")
    try:
        # Absolute path to updater
        updater_path = os.path.abspath(UPDATER_NAME)
        print(f"Updater path: {updater_path}")

        # Run the updater and wait for it to complete
        result = subprocess.run([updater_path], check=True)
        print(f"Updater completed with return code: {result.returncode}")

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
