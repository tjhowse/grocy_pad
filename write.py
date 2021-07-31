#!/usr/bin/python

import os
import hashlib
import subprocess
import click

def get_digest(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


@click.command()
@click.option('--device', default='/dev/ttyS3', help='Serial device.', show_default=True)
@click.option('--kill_screen', default=True, help='Kill all running "screen" sessions before flashing.', show_default=True)
@click.option('--force', default=False, help='Skip already-flashed-to-device check.', show_default=True)
@click.option('--target', default='./src/', help='The directory holding the files to flash.', show_default=True)
def flash_to_micropython(device, kill_screen, force, target):
    """
        Flash the given directory to the given device.
        Skip files that have already been flashed to the device based on a local cache.
        Run pylint against the files first and warn.
    """
    if kill_screen:
        try:
            subprocess.check_output(['pkill', 'screen'])
        except subprocess.CalledProcessError:
            pass

    flashed = os.listdir("./flashed")
    toFlash = os.listdir("./src")
    for file in toFlash:
        if file in flashed and (get_digest("./flashed/" + file) == get_digest("./src/" + file)) and not force:
            print("File " + file + " already flashed")
            continue
        if not file.endswith(".py"):
            continue
        print("Updating " + file)
        subprocess.call(['pylint', '-E', target + file, '-d', 'E1101,E0401'])
        try:
            subprocess.check_output(['ampy', '-p', device, 'put', target + file])
            subprocess.check_output(['cp', '-r', target + file, './flashed/' + file])
            print("Updated " + file)
        except:
            print("Error updating " + file)

if __name__ == '__main__':
    flash_to_micropython()