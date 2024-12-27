import argparse
import logging
import os
import sys
import traceback
from hashlib import sha256
from pathlib import Path
from urllib import request

# private
from network_download import CustomFetcher
from progress_hook import ProgressWindow
from new_update import launch_update_dialog

from tuf.api.exceptions import DownloadError, RepositoryError
from tuf.ngclient import Updater

# constants
DOWNLOAD_DIR = "./downloads"
CLIENT_EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_metadata_dir(base_url: str) -> str:
    """build a unique and reproducible directory name for the repository url"""
    name = sha256(base_url.encode()).hexdigest()[:8]
    # TODO: Make this not windows hostile?
    return f"./client-tuf-metadata/{name}"


def init_tofu(base_url: str) -> bool:
    """Initialize local trusted metadata (Trust-On-First-Use) and create a
    directory for downloads"""
    metadata_dir = build_metadata_dir(base_url)

    if not os.path.isdir(metadata_dir):
        os.makedirs(metadata_dir)

    root_url = f"{base_url}/metadata/1.root.json"
    try:
        request.urlretrieve(root_url, f"{metadata_dir}/root.json")
    except OSError:
        print(f"Failed to download initial root from {root_url}")
        return False

    print(f"Trust-on-First-Use: Initialized new root in {metadata_dir}")
    return True


def download(base_url: str, target: str) -> bool:
    """
    Download the target file using ``ngclient`` Updater.

    The Updater refreshes the top-level metadata, gets the target information,
    verifies if the target is already cached, and if not cached,
    downloads the target file.

    Returns:
        A boolean indicating if the process was successful.
    """
    metadata_dir = build_metadata_dir(base_url)

    if not os.path.isfile(f"{metadata_dir}/root.json"):
        print(
            "Trusted local root not found. Use 'tofu' command to "
            "Trust-On-First-Use or copy trusted root metadata to "
            f"{metadata_dir}/root.json"
        )
        return False

    print(f"Using trusted root in {metadata_dir}")

    # Ensure download directory exists
    if not os.path.isdir(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

    try:
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

        # Target is not cached; ask user if they want to download it
        print(f"Target {target} is missing and requires downloading.")
        user_choice = launch_update_dialog()  # Show dialog and wait for user choice

        if user_choice == True:
            print("Proceeding with the update...")

            # Initialize a progress window only after the user chooses to update
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
        else:
            print("User chose to skip the update.")
            return False

    except (OSError, RepositoryError, DownloadError) as e:
        print(f"Failed to download target {target}: {e}")
        if logging.root.level < logging.ERROR:
            traceback.print_exc()
        return False




def main() -> None:
    """Main TUF Client Example function"""

    client_args = argparse.ArgumentParser(description="TUF Client Example")

    # Global arguments
    client_args.add_argument(
        "-v",
        "--verbose",
        help="Output verbosity level (-v, -vv, ...)",
        action="count",
        default=0,
    )

    client_args.add_argument(
        "-u",
        "--url",
        help="Base repository URL",
        default="http://127.0.0.1:8001",
    )

    # Sub commands
    sub_command = client_args.add_subparsers(dest="sub_command")

    # Trust-On-First-Use
    sub_command.add_parser(
        "tofu",
        help="Initialize client with Trust-On-First-Use",
    )

    # Download
    download_parser = sub_command.add_parser(
        "download",
        help="Download a target file",
    )

    download_parser.add_argument(
        "target",
        metavar="TARGET",
        help="Target file",
    )

    command_args = client_args.parse_args()

    if command_args.verbose == 0:
        loglevel = logging.ERROR
    elif command_args.verbose == 1:
        loglevel = logging.WARNING
    elif command_args.verbose == 2:
        loglevel = logging.INFO
    else:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)

    # initialize the TUF Client Example infrastructure
    if command_args.sub_command == "tofu":
        if not init_tofu(command_args.url):
            return "Failed to initialize local repository"
    elif command_args.sub_command == "download":
        if not download(command_args.url, command_args.target):
            return f"Failed to download {command_args.target}"
    else:
        client_args.print_help()


if __name__ == "__main__":
    sys.exit(main())
