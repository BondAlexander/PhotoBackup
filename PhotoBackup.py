#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import os
import sys
import time
import zipfile
import filecmp
import hashlib


types = ['png', 'jpeg', 'jpg', 'mp4', 'gif', 'heif', 'HEIC', 'mov']
hashes = []

def loadHashes():
    if(os.path.exists(".hash_cache")):
        for line in open(".hash_cache", 'r').read().split('\n'):
            hashes.append(line)
        return
    else:
        open(".hash_cache", "a")
        populateHashes()


def populateHashes():
    if(os.path.exists("PhotoLibrary.zip")):
        with zipfile.ZipFile('PhotoLibrary.zip', 'a') as myzip:
            for file in myzip.namelist():
                try:
                    myzip.extract(file)
                    hashes.append(hashFile(file))
                    os.remove(file)
                except zipfile.BadZipFile as e:
                    print(f"Couldn\'t hash {file}\nReason: {e}")

def recordHashes():
    for hash in hashes:
        with open(".hash_cache", 'a') as hash_cache:
            hash_cache.write(hash + '\n')


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
                continue
            print(f"Found new photo: {file}")
            creation_time   = time.gmtime(os.path.getmtime(f"{target_dir}/{name}{extension}"))
            folder_name     = time.strftime('%Y %m', creation_time)
            file_name       = time.strftime('%d %H.%M.%S', creation_time)
            with zipfile.ZipFile('PhotoLibrary.zip', 'a') as myzip:
                version = 1
                while(True):
                    if(f'{folder_name} {file_name}_{version}.{extension[1:]}' in myzip.namelist()):
                        version = version + 1
                    else:
                        hash = hashFile(f"{target_dir}/{file}")
                        myzip.write(f"{target_dir}/{file}",arcname=f'{folder_name} {file_name}_{version}.{extension[1:]}')
                        hashes.append(hash)
                        break


# -------========MAIN========-------
print("Populating hashes...")
loadHashes()
print("Done.")
photoBackupOSX("/Users/bondalexander/Desktop/PhotoLibrary")
#photoBackupOSX("/Users/bondalexander/Downloads/Backup")
recordHashes()
