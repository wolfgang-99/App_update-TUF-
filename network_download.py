from tuf.ngclient.fetcher import FetcherInterface
from tuf.api.exceptions import DownloadError, DownloadHTTPError
from typing import Iterator
import requests


def progress_hook(bytes_downloaded: int, bytes_expected: int):

    if bytes_expected == 0:  # Avoid division by zero
        print("\rUnknown progress: total size is 0", end="")
        return

    progress_percent = (bytes_downloaded / bytes_expected) * 100
    print(f'\r{progress_percent:.1f}%', end='')
    if bytes_downloaded >= bytes_expected:
        print("\nDownload complete.")


class CustomFetcher(FetcherInterface):
    def __init__(self, progress_hook, chunk_size=4096, timeout=30):
        self.progress_hook = progress_hook
        self.chunk_size = chunk_size
        self.timeout = timeout

    def _fetch(self, url: str) -> Iterator[bytes]:
        try:
            with requests.get(url, stream=True, timeout=self.timeout) as response:
                if response.status_code != 200:
                    raise DownloadHTTPError(f"HTTP error {response.status_code} for {url}", status_code=response.status_code)


                content_length = int(response.headers.get("Content-Length", 0))
                downloaded_bytes = 0

                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    downloaded_bytes += len(chunk)
                    self.progress_hook(downloaded_bytes, content_length)
                    yield chunk

        except requests.RequestException as e:
            raise DownloadError(f"Failed to fetch {url}: {str(e)}")
