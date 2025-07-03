import os
import urllib.request
import zipfile
import subprocess
import re
from pathlib import Path


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
        dest_folder (str | Path): Directory path (string or Path) where the file will be saved/extracted.
        unzip (bool): If True, extract the ZIP archive into `dest_folder` after download. Defaults to True.
        delete_zip (bool): If True, delete the downloaded ZIP file after extraction. Defaults to True.

    Raises:
        URLError, HTTPError: If downloading the file fails.
        zipfile.BadZipFile: If the downloaded file is not a valid ZIP archive.
    """
    # Normalize destination to Path
    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    # Determine zip filename and full path
    zip_name = os.path.basename(url)
    zip_path = dest_folder / zip_name

    print(f"Downloading from {url}...")
    # urllib expects a string path
    urllib.request.urlretrieve(url, str(zip_path))

    if unzip:
        print(f"Extracting to {dest_folder}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)

    if delete_zip:
        zip_path.unlink()
        print(f"Deleted zip file: {zip_path}")

    print("Done.")


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
    # 1) Read & normalize your deps file
    lines = Path(deps_file).read_text().splitlines()
    raw = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]

    pkgs = []
    for ln in raw:
        # drop version constraints and anything after '|'
        name = re.sub(r"\s*\([^)]*\)", "", ln).split("|",1)[0].strip()
        pkgs.append(name)

    if not pkgs:
        print("No packages to install.")
        return

    # 2) Refresh once
    subprocess.run(["sudo", "apt-get", "update"], check=True)

    # 3) Resolve each pkg
    to_install = []
    for pkg in pkgs:
        print(f"→ Checking {pkg}")
        res = subprocess.run(
            ["sudo", "apt-get", "install", "--simulate", pkg],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # if simulate succeeded without errors, we can install pkg
        if res.returncode == 0:
            to_install.append(pkg)
            continue

        # otherwise, look for “Note, selecting 'realpkg' instead of 'pkg'”
        m = re.search(r"Note, selecting '([^']+)' instead of '%s'" % re.escape(pkg),
                      res.stderr)
        if m:
            real = m.group(1)
            print(f"    ↳ Virtual {pkg} → {real}")
            to_install.append(real)
        else:
            print(f"    ⚠️  Skipping {pkg}: no candidate")

    if not to_install:
        print("No installable packages found.")
        return

    # 4) Install them all
    print("Installing:", ", ".join(to_install))
    subprocess.run(
        ["sudo", "apt-get", "install", "-y", *to_install],
        check=True
    )
    print("Done.")


if __name__ == "__main__":
    install_deb_deps("chrome-headless-shell-linux64/deb.deps")
