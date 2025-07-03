import os
import urllib.request
import zipfile
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def download_and_extract_zip(
    url: str,
    dest_folder: str | Path,
    unzip: bool = True,
    delete_zip: bool = True
) -> None:
    """
    Works on Windows, macOS, and Ubuntu.
    Download a ZIP file from the given URL into the specified folder (string or Path),
    optionally extract it, and optionally remove the archive.

    Args:
        url (str): URL of the ZIP file to download.
        dest_folder (str | Path): Directory path where the file will be saved/extracted.
        unzip (bool): If True, extract the ZIP archive into `dest_folder` after download.
        delete_zip (bool): If True, delete the downloaded ZIP file after extraction.

    Raises:
        URLError, HTTPError: If downloading the file fails.
        zipfile.BadZipFile: If the file is not a valid ZIP archive.
    """
    # 1) Ensure dest_folder is a Path and exists
    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    # 2) Figure out a safe filename from the URL
    zip_name = Path(urlparse(url).path).name
    zip_path = dest_folder / zip_name

    print(f"→ Downloading {url} …")
    urllib.request.urlretrieve(url, str(zip_path))

    if unzip:
        print(f"→ Extracting to {dest_folder} …")
        with zipfile.ZipFile(zip_path, 'r') as archive:
            archive.extractall(dest_folder)

    if delete_zip:
        zip_path.unlink()
        print(f"→ Removed archive {zip_path}")

    print("✅ Done.")


def ensure_paths(
    dirs_list: list[str | Path] | None = None,
    file_paths: list[str | Path] | None = None,
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
        dirs_list:     List of directories (str or Path) to check.
        file_paths:    List of file paths (str or Path) to check.
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
                dir_path = Path(d)
                if not dir_path.exists():
                    if create_dir:
                        dir_path.mkdir(parents=True, exist_ok=True)
                    else:
                        errors.append(
                            f"Directory does not exist: {dir_path}. Create it or set create_dir=True."
                        )
                        continue
                if not os.access(dir_path, os.R_OK):
                    errors.append(
                        f"Directory is not readable: {dir_path}. Set read permission: chmod +r '{dir_path}'"
                    )
                if not os.access(dir_path, os.W_OK):
                    errors.append(
                        f"Directory is not writable: {dir_path}. Set write permission: chmod +w '{dir_path}'"
                    )
            except Exception as e:
                errors.append(f"Error handling directory '{d}': {e}")

    # --- Check files ---
    if file_paths:
        for f in file_paths:
            try:
                file_path = Path(f)
                parent = file_path.parent or Path('.')
                if not parent.exists():
                    if create_file:
                        parent.mkdir(parents=True, exist_ok=True)
                    else:
                        errors.append(
                            f"Parent directory does not exist: {parent}. Create it or set create_file=True."
                        )
                        continue
                if not file_path.exists():
                    if create_file:
                        file_path.touch()
                    else:
                        errors.append(
                            f"File does not exist: {file_path}. Create it or set create_file=True."
                        )
                        continue
                if not os.access(file_path, os.R_OK):
                    errors.append(
                        f"File is not readable: {file_path}. Set read permission: chmod +r '{file_path}'"
                    )
                if not os.access(file_path, os.W_OK):
                    errors.append(
                        f"File is not writable: {file_path}. Set write permission: chmod +w '{file_path}'"
                    )
                if not os.access(file_path, os.X_OK):
                    errors.append(
                        f"File is not executable: {file_path}. Set execute permission: chmod +x '{file_path}'"
                    )
            except Exception as e:
                errors.append(f"Error handling file '{f}': {e}")

    return False if not errors else "\n".join(errors)


def install_deb_deps(deps_file: str | Path) -> None:
    """
    Read package names from a `deb.deps` file (one per line)
    and run `sudo apt-get update` and `sudo apt-get install -y` on them.

    Args:
        deps_file: Path (string or Path) to the `deb.deps` file.

    Raises:
        CalledProcessError: If subprocess commands fail.
    """
    deps_path = Path(deps_file)
    pkgs = [line.strip() for line in deps_path.read_text().splitlines() if line.strip()]
    if not pkgs:
        print("No packages to install.")
        return

    # Update package lists and install in one go
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", *pkgs], check=True)