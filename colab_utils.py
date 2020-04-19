# Some Colab utils taken from gpt2simple by Max Woolf
# License at https://github.com/minimaxir/gpt-2-simple/blob/master/LICENSE

import os
import shutil
import sys
import tarfile
# If in Google Colaboratory
try:
    from google.colab import drive
except:
    pass

def mount_gdrive():
    """Mounts the user's Google Drive in Colaboratory."""
    assert 'google.colab' in sys.modules, "You must be in Colaboratory to mount your Google Drive"
    if not is_mounted():
        drive.mount("/content/drive")

def is_mounted():
    """Returns whether the Google Drive is mounted."""
    return os.path.isdir("/content/drive")

def assert_mounted():
    """Asserts if the Google Drive is mounted."""
    assert is_mounted(), "You must mount first using mount_gdrive()"

def get_tarfile_name(checkpoint_folder):
    """Converts a folder path into a filename for a .tar archive"""
    tarfile_name = checkpoint_folder.replace(os.path.sep, "_") + ".tar"
    return tarfile_name

def copy_checkpoint_to_gdrive(checkpoint_path, make_tar=True):
    """Copies the checkpoint folder to a mounted Google Drive."""
    assert_mounted()
    base_path, folder_name = os.path.split(checkpoint_path)

    if not make_tar:
        drive_path = "/content/drive/My Drive/" + folder_name
        shutil.copytree(checkpoint_path, drive_path)
    else:
        tar_path = checkpoint_path + ".tar"
        drive_path = "/content/drive/My Drive/" + folder_name + ".tar"
        # Reference: https://stackoverflow.com/a/17081026
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(checkpoint_path)
        shutil.copyfile(tar_path, drive_path)

    print(f"Copied {checkpoint_path} to {drive_path}")

def copy_checkpoint_from_gdrive(folder_or_tar_name, checkpoints_path="/runs"):
    """Copies the checkpoint folder from a mounted Google Drive."""
    assert_mounted()
    folder_name = os.path.splitext(folder_or_tar_name)[0]
    checkpoint_path = os.path.join(checkpoints_path, folder_name)
    drive_path = "/content/drive/My Drive/" + folder_or_tar_name

    if os.path.isdir(drive_path):
        shutil.copytree(drive_path, checkpoint_path)
    else:
        tar_path = checkpoint_path + ".tar"
        shutil.copyfile(drive_path, tar_path)
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall()

    print(f"Copied {drive_path} to {checkpoint_path}")

def copy_file_to_gdrive(file_path):
    """Copies a file to a mounted Google Drive."""
    assert_mounted()
    drive_path = "/content/drive/My Drive/" + file_path
    shutil.copyfile(file_path, drive_path)
    print(f"Copied {file_path} to {drive_path}")

def copy_file_from_gdrive(file_path):
    """Copies a file from a mounted Google Drive."""
    assert_mounted()
    drive_path = "/content/drive/My Drive/" + file_path
    shutil.copyfile(drive_path, file_path)
    print(f"Copied {drive_path} to {file_path}")
