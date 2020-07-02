from pymel.core import *
import maya.mel as mel
import maya.cmds as mc
import random as r
import shutil, subprocess, sys, getpass, time, os, platform

##############################################################################################

# Install required packages

# install: Install a package by calling sys and pip.
# Takes in a str package and calls "pip install package". 
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

##############################################################################################

# simple cube for testing
def createPolyCube(*args):
    mc.polyCube()

# Create a basic Yes/No dialog.
def confirm_box():
    mc.confirmDialog(title='Confirm', message='Are you sure?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')

# lol
def praise_cody():
    mc.confirmDialog(title='AnimKit Loaded Successfully', 
    message='Praise the Savor of lights, Mighty king of squirrels, Finders of all Paths, and the creator of all clowns, Cody!', 
    button=['Anim!'], defaultButton='Anim!', dismissString='Anim!')



############################################################################################
# Load Animschool Picker
# win_support: Convert filepath acquired by os to appropriate windows file pathformat.
# Takes in a str filepath and returns a str with all the \ replaced with /
def win_support(filepath):
    return filepath.replace('\\','/')

# get_latest_version: Get the latest version of Maya.
# Takes in a str MAYA_FOLDER and returns a str of VERSION in Maya, e.g. "2020"
def get_latest_version(MAYA_FOLDER):
    version_folders = []
    for x in os.listdir(MAYA_FOLDER):
        try:
            folder = int(x)
            version_folders += [folder]
        except: pass
    return str(max(version_folders))
# Define OS type, Legacy.
if "Darwin" in str(platform.system()):
    # macOS is actually not supported for now because I am too lazy.
    OS_TYPE = "Mac"
    USER = os.environ["HOME"]
    MAYA_FOLDER = "{0}/Library/Preferences/Autodesk/maya/".format(USER)
    DESKTOP = os.path.expanduser("~/Desktop")
else:
    OS_TYPE = "Windows"
    USER = win_support(os.getenv("USERPROFILE"))
    MAYA_FOLDER = "{0}/Documents/maya/".format(USER)
    DESKTOP = USER + '/Desktop'
    
# MAYA_VERSION: e.g. 2020
MAYA_VERSION = get_latest_version(MAYA_FOLDER)

# MAYA_SCRIPT_FOLDER: Where maya stores all its scripts
MAYA_SCRIPT_FOLDER = "{0}{1}/scripts/".format(MAYA_FOLDER,MAYA_VERSION)


def load_animschool_picker():
    mc.loadPlugin(MAYA_SCRIPT_FOLDER + 'AnimSchoolPicker.mll')
    mel.eval('AnimSchoolPicker();')

############################################################################################