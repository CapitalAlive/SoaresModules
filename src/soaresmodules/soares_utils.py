import os
import urllib.request
import zipfile


def download_and_extract_zip(
    url: str,
    dest_folder: str,
    unzip: bool = True,
    delete_zip: bool = True
):
    """
    Works on Windows, MAC and Ubuntu.
    Download a ZIP file from the given URL into the specified folder, optionally extract it, and optionally remove the archive.

    Args:
        url (str): URL of the ZIP file to download.
        dest_folder (str): Path to the directory where the file will be saved (and extracted).
        unzip (bool): If True, extract the ZIP archive into `dest_folder` after download. Defaults to True.
        delete_zip (bool): If True, delete the downloaded ZIP file after extraction. Defaults to True.

    Raises:
        URLError, HTTPError: If downloading the file fails.
        zipfile.BadZipFile: If the downloaded file is not a valid ZIP archive.
    """
    os.makedirs(dest_folder, exist_ok=True)
    zip_name = os.path.basename(url)
    zip_path = os.path.join(dest_folder, zip_name)

    print(f"Downloading from {url}...")
    urllib.request.urlretrieve(url, zip_path)

    if unzip:
        print(f"Extracting to {dest_folder}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)

    if delete_zip:
        os.remove(zip_path)
        print(f"Deleted zip file: {zip_path}")

    print("Done.")


def ensure_paths_editable(paths_list):
    """
    For each path in `paths_list`, ensure its parent dir exists,
    create the file if it doesn't exist, and verify it's writable.
    Returns the first error (Exception or str), or False if all OK.
    """
    for path in paths_list:
        try:
            # 1) make sure parent directory exists
            parent = os.path.dirname(path) or '.'
            os.makedirs(parent, exist_ok=True)
            # 2) touch the file if it doesn't exist
            if not os.path.exists(path):
                with open(path, 'a'):
                    pass
            # 3) verify writability
            if not os.access(path, os.W_OK):
                return f"Path not writable: {path}"

        except Exception as e:
            return e

    return False
