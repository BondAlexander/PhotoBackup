#!/usr/path/env python
import os
import sys
import time
import argparse
import zipfile
import filecmp
import hashlib
import threading
import math

types = ['png', 'jpeg', 'jpg', 'mp4', 'gif', 'heif', 'HEIC', 'mov', 'm4v']
hashes = []
bytes_copied = 0

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
                    pass
                    #print(f"Couldn\'t hash {file}")

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

def convertByteSize(bytes):
    text_string = ""
    size_float = float(bytes)
    unit = "b"
    byte_sizes = ["B", "KB", "MB", "GB", "TB"]
    for size in byte_sizes:
        if(size_float / 1000 < 1):
            unit = size
            break
        else:
            size_float = size_float / 1000
    return f"{int(size_float * 100) / 100.0} {unit}"

def photoBackupOSX(target_dir):
    global args
    for file in os.listdir(target_dir):
        name, extension = os.path.splitext(file)
        #Recursive Step
        if(os.path.isdir(f"{target_dir}/{file}")):
            photoBackupOSX(f"{target_dir}/{file}")
        #Only captures images
        elif(extension[1:] in types):
            #ignore duplicates
            if(hashFile(f"{target_dir}/{file}") in hashes):
                if(args.delete):
                        os.remove(f"{target_dir}/{file}")
                continue
            
            #Gather file info
            creation_time   = time.gmtime(os.path.getmtime(f"{target_dir}/{name}{extension}"))
            folder_name     = time.strftime('%b %Y', creation_time)
            file_name       = time.strftime('%d %H.%M.%S', creation_time)
            global bytes_copied
            bytes_copied    = bytes_copied + os.path.getsize(f"{target_dir}/{name}{extension}")
            sys.stdout.write(f"\tFound new photo: {file} Bytes Copied: " + convertByteSize(bytes_copied) + "                             \r")
            sys.stdout.flush()
            #Todo Create check if safe to add file

            
            version = 1
            with zipfile.ZipFile('PhotoLibrary.zip', 'a') as myzip:
                while(True):
                    if(f'{folder_name}/{file_name}_{version}.{extension[1:]}' in myzip.namelist()):
                        version = version + 1
                    else:
                        hash = hashFile(f"{target_dir}/{file}")
                        
                        myzip.write(f"{target_dir}/{file}",arcname=f'{folder_name}/{file_name}_{version}.{extension[1:]}')
                        hashes.append(hash)
                        if(args.delete):
                            os.remove(f"{target_dir}/{file}")
                        break
    

def createArgs():
    parser = argparse.ArgumentParser(description="PhotoBackup Arguments")
    parser.add_argument("-D", "--delete", action="store_true")
    parser.add_argument("-p", "--path")
    
    return parser.parse_args()


# -------========MAIN========-------
args = createArgs()
print("Populating hashes...")
loadHashes()
print("Done.")

photoBackupOSX(args.path)

#photoBackupOSX("/Users/bondalexander/Downloads/Backup")
#recordHashes()
