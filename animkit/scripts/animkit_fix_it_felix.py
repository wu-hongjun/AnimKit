from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import shutil, subprocess, sys, getpass, time, os, platform
from mtoa.cmds.arnoldRender import arnoldRender
from os import listdir
from os.path import isfile, join


# Version Info
VERSION = "2.2.0"
UPDATE = "Aug 26, 2020"
NEW = "Fix-it-Felix integrates all the small fixes and organize them in a same place."

# =================================================== FixNURBS ===================================================
def rebuild_surface_cmd(surface, caching = "1", 
                        replaceOriginal = "1", 
                        endKnots = "1", 
                        keepRange = "0", 
                        keepControlPoints = "0", 
                        keepCorners = "0"):
    
    general_cmds = " -ch " + caching + " -rpo " + replaceOriginal + " -end " + endKnots
    keep_cmds = " -kr " + keepRange + " -kcp " + keepControlPoints + " -kc " + keepCorners
    surface_cmd = " \"" + surface + "\""
    
    cmd = "rebuildSurface" + general_cmds + keep_cmds + surface_cmd
    return cmd


def fix_broken_NURBS(self):
    surface_list = cmds.ls(type='nurbsSurface')
    for surface in surface_list:
        command = rebuild_surface_cmd(surface)
        try:
            mel.eval(command) # TODO: Write catchQuiet correctly to surpress warnings.
        except RuntimeError:
            print("[Fix-it-Felix] Failed to rebuild the following surface: " + surface)
        except:
            print("[Fix-it-Felix] Unknown error occured while trying to execute the following command: " + command)
    print("[Fix-it-Felix] Fix Broken NURBS - Successfully rebuilt all avaliable NURBS Surfaces.")

# =================================================== FixArnold ===================================================
def fix_defaultArnoldDriver_pre(self):
    '''
    Sets the defaultArnoldDriver.pre to its original state of "".
    '''
    cmds.setAttr("defaultArnoldDriver.pre", "", type="string")
    print("[Fix-it-Felix] Fix Arnold Global - Successfully fixed defaultArnoldDriver.pre settings to original.")

def load_arnold_plugin(self):
    mel.eval("loadPlugin mtoa.mll;")
    print("[Fix-it-Felix] Load Arnold Plugin - Attempted to load mtoa.mll Arnold plugin.")

# =================================================== FixCamera ===================================================
def create_render_cam_from_view(self):
    cameraTransform = cmds.modelEditor(cmds.getPanel(withLabel = 'Persp View'), query = True, camera = True)
    cameraShape = cmds.listRelatives(cameraTransform, type = 'camera')[0]
    newCameraName = "render_cam"

    cmds.duplicate(cameraShape, name = newCameraName)
    cmds.showHidden(newCameraName)
    cmds.select(newCameraName, replace = True)

# =================================================== FixScene ===================================================

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

