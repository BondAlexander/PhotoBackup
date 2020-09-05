#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import os
import sys
import time
import zipfile
import filecmp
import hashlib


types = ['png', 'jpeg', 'jpg', 'mp4', 'gif', 'heif', 'HEIC', 'mov']
hashes = []

def hashFile(file_name):
    BLOCK_SIZE = 65536
    file_hash = hashlib.sha256()
    with open(file_name, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)
    hash = file_hash.hexdigest()
    return str(hash)


def photoBackupOSX(target_dir):
    for file in os.listdir(target_dir):
        name, extension = os.path.splitext(file)
        #Recursive Step
        if(os.path.isdir(f"{target_dir}/{file}")):
            photoBackupOSX(f"{target_dir}/{file}")
        #Only captures images
        elif(extension[1:] in types):
            #ignore duplicates
            if(hashFile(f"{target_dir}/{file}") in hashes):
                print("ignoring dupe")
                continue

            creation_time   = time.gmtime(os.path.getmtime(f"{target_dir}/{name}{extension}"))
            folder_name     = time.strftime('%Y %m', creation_time)
            file_name       = time.strftime('%d %H.%M.%S', creation_time)
            print(f'{folder_name}/{file_name}.{extension[1:]}')
            with zipfile.ZipFile('PhotoLibrary.zip', 'a') as myzip:
                version = 1
                while(True):
                    if(f'{folder_name} {file_name}_{version}.{extension[1:]}' in myzip.namelist()):
                        version = version + 1
                    else:
                        hashes.append(hashFile(f"{target_dir}/{file}"))
                        myzip.write(f"{target_dir}/{file}",arcname=f'{folder_name} {file_name}_{version}.{extension[1:]}')
                        break


# -------========MAIN========-------
#photoBackupOSX("/Users/bondalexander/Desktop/Pictures")
photoBackupOSX("/Users/bondalexander/Downloads/Backup")
