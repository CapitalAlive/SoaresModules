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


import os

def ensure_paths(
    dirs_list: list[str] | None = None,
    file_paths: list[str] | None = None,
    create_dir: bool = False,
    create_file: bool = False
) -> bool | str:
    """
    Ensure that the given directories and files exist and meet access requirements.

    Directories:
      - If a dir in `dirs_list` does not exist:
          • Create it if `create_dir` is True
          • Otherwise report an error.
      - Verify each dir is readable and writable.

    Files:
      - For each path in `file_paths`:
          1. Ensure its parent directory exists:
             • Create parents if `create_file` is True
             • Otherwise report an error.
          2. If the file itself is missing:
             • Create it if `create_file` is True
             • Otherwise report an error.
          3. Verify the file is readable, writable, and executable.

    Args:
        dirs_list:     List of directories to check.
        file_paths:    List of file paths to check.
        create_dir:    If True, create missing directories.
        create_file:   If True, create missing files (and their parents).

    Returns:
        False if all checks pass;
        otherwise a newline-separated string describing every error found.
    """
    errors: list[str] = []

    # --- Check directories ---
    if dirs_list:
        for d in dirs_list:
            try:
                if not os.path.exists(d):
                    if create_dir:
                        os.makedirs(d, exist_ok=True)
                    else:
                        errors.append(f"Directory does not exist: {d}")
                        continue
                if not os.access(d, os.R_OK):
                    errors.append(f"Directory is not readable: {d}")
                if not os.access(d, os.W_OK):
                    errors.append(f"Directory is not writable: {d}")
            except Exception as e:
                errors.append(f"Error handling directory {d}: {e}")

    # --- Check files ---
    if file_paths:
        for f in file_paths:
            try:
                parent = os.path.dirname(f) or '.'
                if not os.path.exists(parent):
                    if create_file:
                        os.makedirs(parent, exist_ok=True)
                    else:
                        errors.append(f"Parent directory does not exist: {parent}")
                        continue

                if not os.path.exists(f):
                    if create_file:
                        open(f, 'a').close()
                    else:
                        errors.append(f"File does not exist: {f}")
                        continue

                if not os.access(f, os.R_OK):
                    errors.append(f"File is not readable: {f}")
                if not os.access(f, os.W_OK):
                    errors.append(f"File is not writable: {f}")
                if not os.access(f, os.X_OK):
                    errors.append(f"File is not executable: {f}")
            except Exception as e:
                errors.append(f"Error handling file {f}: {e}")

    return False if not errors else "\n".join(errors)
