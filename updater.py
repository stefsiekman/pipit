import requests
import io
import os
import tempfile
import json
import zipfile
import shutil


LATEST_RELEASE_URL = \
    "https://api.github.com/repos/stefsiekman/pipit/releases/latest"
INFO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "version-info.json")

KEY_ACTIVE_TEMP_DIR = "active_temp_dir"
KEY_INSTALLED = "installed"


def log(msg):
    print(f"AutoUpdater: {msg}")


def latest_release_info():
    log("Downloading release info...")
    response = requests.get(LATEST_RELEASE_URL)

    if response is None:
        return

    response_json = response.json()

    return response_json["name"], response_json["zipball_url"]


def read_version_info():
    # Nothing if no current version exists
    if not os.path.exists(INFO_FILE):
        return

    info_file = open(INFO_FILE, "r")
    return json.load(info_file)


def write_version_info(info):
    json.dump(info, open(INFO_FILE, "w"))


def update_version_info_key(key, value):
    old_info = read_version_info() or dict()
    old_value = old_info[key] if key in old_info else None
    old_info[key] = value
    write_version_info(old_info)
    return old_value


def update_required_zip():
    version_info = read_version_info()

    latest_release = latest_release_info()

    if latest_release is None:
        log("Latest release info could not be downloaded")
        return

    log(f"Latest release: {latest_release[0]}")

    if version_info and KEY_INSTALLED in version_info:
        installed_version = version_info[KEY_INSTALLED]
        log(f"Current version is {installed_version}")

        if installed_version == latest_release[0]:
            log("Already on latest version")
            return

        # TODO: check if the version info indicates a >= version than release
        # optionally return None
    else:
        log("No current version information known")

    return latest_release


def remove_temp_dir(path):
    # Do nothing if the dir does not even exist anymore
    if not os.path.exists(path):
        return

    shutil.rmtree(path)
    log("Removed temp dir")


def activate_new_temp_dir():
    path = tempfile.mkdtemp()
    old_temp = update_version_info_key(KEY_ACTIVE_TEMP_DIR, path)

    if old_temp:
        remove_temp_dir(old_temp)

    return path


def download_zip(url):
    log("Downloading release...")
    response = requests.get(url)

    if response is None:
        return

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    # Extract the zip to a temp directory
    temp_dir = activate_new_temp_dir()
    zip_file.extractall(temp_dir)
    code_dir = zip_file.filelist[0].filename
    zip_file.close()

    return temp_dir, os.path.join(temp_dir, code_dir)


def download_update():
    update_required_info = update_required_zip()

    if not update_required_info:
        return None

    release_version, release_zip = update_required_info

    if release_zip is None:
        log("No update will be installed")
        return

    log(f"Updating to new release {release_version}...")

    temp_dir, code_dir = download_zip(release_zip)
    log(f"Downloaded to {code_dir}")
    return temp_dir, code_dir, release_version


def move_download(from_path, to_path):
    for file in os.listdir(from_path):
        shutil.move(os.path.join(from_path, file), os.path.join(to_path, file))


def install_update():
    # Install update
    downloaded_info = download_update()
    if not downloaded_info:
        return

    temp_dir, code_dir, new_version = downloaded_info
    prog_dir = os.path.dirname(os.path.abspath(__file__))
    log("Moving files...")
    move_download(code_dir, prog_dir)

    # Remove the temp dir
    remove_temp_dir(temp_dir)
    update_version_info_key(KEY_ACTIVE_TEMP_DIR, None)

    # Update installed version
    update_version_info_key(KEY_INSTALLED, new_version)
    log(f"Updated to {new_version}")


if __name__ == "__main__":
    install_update()


