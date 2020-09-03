#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import os
import sys
import time


types = ['png', 'jpeg', 'jpg', 'mv4']

def photoBackupOSX(target_dir):
    for(file in os.listdir(target_dir))
        name, extension = os.path.splitext(file)

        #Recursive Step
        if(os.path.isdir(file)):
            photoBackupOSX(file)
        #Only captures images
        elif(extension in types):
