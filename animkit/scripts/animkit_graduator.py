from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import shutil, subprocess, sys, getpass, time, os, platform

##############################################################################################

def graduator(self):
    sn = sceneName()
    
    if sn == '':
        self.showErrorWindow("ERROR!\nThis scene is not saved yet.")
        return None

    if not check_student():
        prompt_error()
    else:
        orig = current_dir()
        prompt_info()
        save_backup()
        
        bkup = current_dir()
        graduate(bkup, orig) # Use the backup version aka student version to overwrite the original version
        
        prompt_exit()


def check_student():
    sn = sceneName()
    dir = sn.parent
    name = os.path.basename(sn).split('.')[0]
    currentDir = os.path.join(dir, name + '.ma').replace('\\', '/')

    ma_file = open(currentDir, "r")
    file_content = ma_file.read()

    status = "fileInfo \"license\" \"student\";" in file_content
    print("[GRADUATOR] Student Status: ", status)
    return status

def current_dir():
    sn = sceneName()
    dir = sn.parent
    name = os.path.basename(sn).split('.')[0]
    return os.path.join(dir, name + '.ma').replace('\\', '/')

def save_backup():
    sn = sceneName()
    dir = sn.parent
    name = os.path.basename(sn).split('.')[0]
    bkupDir = os.path.join(dir, name + '_bkup.ma').replace('\\', '/')

    cmds.file(rename = bkupDir)
    cmds.file(save = True)
    print("[GRADUATOR] Successfully saved backup file in: ", bkupDir)

def graduate(input_ma, output_ma):
    ma_file = open(input_ma, "r")
    file_content = ma_file.read()
    
    student_version = "fileInfo \"license\" \"student\";"
    target_version = ""
    
    if student_version in file_content:
        print("[GRADUATOR]: Found student version info.")
        new_content = file_content.replace(student_version, target_version)
        new_file = open(output_ma, "w")
        new_file.write(new_content)
        print("[GRADUATOR]: Successfully wrote new file without student info in: ", output_ma)
    else:
        print("[GRADUATOR]: Given file: ", input_ma, " is not a student version maya file!")
    
    ma_file.close()
    
def prompt_info():
    cmds.confirmDialog(title='Animkit Graduator: Information', 
        message='Graduator will save the current scene as a backup. After you are prompted to save the current scene simply close Maya and reopen the graduated scene. ', 
        button=['I got it!'], defaultButton='I got it!', dismissString='I got it!')

def prompt_exit():
    cmds.confirmDialog(title='Animkit Graduator: Exit', 
        message='Graduator finished its operation. Please close the current scene and open the new scene.', 
        button=['I got it!'], defaultButton='I got it!', dismissString='I got it!')

def prompt_error():
    cmds.confirmDialog(title='Animkit Graduator: Not a Student File!', 
        message='This is not a file in student version. There\'s nothing to do.', 
        button=['I got it!'], defaultButton='I got it!', dismissString='I got it!')

