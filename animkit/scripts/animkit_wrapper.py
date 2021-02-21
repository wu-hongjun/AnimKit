from pymel.core import *
import maya.mel as mel
import maya.cmds as mc
import random as r
import shutil, subprocess, sys, getpass, time, os, platform
import animkit_tweenMachine

##############################################################################################

def run_mel(script_name):
        '''Runs a given MEL file'''
        print("Running MEL file: " + script_name)
        mel.eval("source " + script_name + ";")

##############################################################################################

# praise Cody
def praise_cody():
    mc.confirmDialog(title='AnimKit Loaded Successfully', 
    message='Praise the Savor of lights, Mighty king of squirrels, Finders of all Paths, and the creator of all clowns, Cody!', 
    button=['Anim!'], defaultButton='Anim!', dismissString='Anim!')

# Load AnimSchool Picker
def load_animschool_picker(self):
    mel.eval("loadPlugin AnimSchoolPicker.mll;")
    mel.eval("AnimSchoolPicker();")

# Load reParent
def load_reParent(self):
    run_mel('reparent_pro_v158.mel')

def load_tweenMachine(self):
    animkit_tweenMachine.start()

# Get PIP
# MAYA_VERSION: e.g. 2020
def get_latest_version(MAYA_FOLDER):
    version_folders = []
    for x in os.listdir(MAYA_FOLDER):
        try:
            folder = int(x)
            version_folders += [folder]
        except: pass
    return str(max(version_folders))

def get_pip(self):
    USER = os.getenv("USERPROFILE").replace('\\','/')
    MAYA_FOLDER = "{0}/Documents/maya/".format(USER)
    MAYA_VERSION = get_latest_version(MAYA_FOLDER)
    MAYA_SCRIPT_FOLDER = "{0}{1}/scripts/".format(MAYA_FOLDER,MAYA_VERSION)


    pip_script_loc = MAYA_SCRIPT_FOLDER + 'animkit_get-pip.py'
    print("[GET PIP] PIP script folder location: " + pip_script_loc)
    execfile(pip_script_loc)
    # print(execfile("C:/Users/hongj/Documents/maya/2020/scripts/animkit_get-pip.py"))


# Install stuff via pip
def install_package_pip(package_name):
    import subprocess
    cmd = "pip install " + package_name
    subprocess.call(cmd)

def try_loop():
    