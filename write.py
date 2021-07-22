#!/usr/bin/python

import os
import hashlib
import subprocess

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

flashed = os.listdir("./flashed")

toFlash = os.listdir("./src")
for file in toFlash:
    if file in flashed and (get_digest("./flashed/" + file) == get_digest("./src/" + file)):
        print("File " + file + " already flashed")
        continue
    try:
        print("Updating " + file)
        subprocess.check_output(['ampy', '-p', '/dev/ttyS3', 'put', './src/' + file])
        subprocess.check_output(['cp', './src/' + file, './flashed/' + file])
        print("Updated " + file)
    except:
        print("Error updating " + file)