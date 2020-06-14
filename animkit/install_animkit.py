##############################################################################################

# install_animkit.py
# Installs animkit shelf into the newest version of maya's /scripts folder.

##############################################################################################
# Import required packages

import time, os, platform, shutil, subprocess, sys

##############################################################################################
# Functions

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

# install_script: helper function for install_shelf. Installs a script into maya's .\scripts folder.
def install_script(script_name):
    target_path = os.path.join(MAYA_SCRIPT_FOLDER, script_name)
    setup_file = ANIMKIT_SCRIPT_FOLDER + "\scripts\\" + script_name
    shutil.copy(setup_file, target_path)
    print("Copied " + script_name + " into: " + target_path)
    
# install_shelf:
# Installs shelf and all the scripts into maya's .\scripts folder. 
def install_shelf():

    # Check if the Maya script folder exists, if not, create one.
    if not os.path.isdir(MAYA_SCRIPT_FOLDER): 
        os.makedirs(MAYA_SCRIPT_FOLDER)
        print("Maya script folder does not exist. Created script folder under: ", MAYA_SCRIPT_FOLDER)
    if os.path.isdir(MAYA_SCRIPT_FOLDER):
        print("Maya script folder already exists under: ", MAYA_SCRIPT_FOLDER)
            
    # Copy setup file into the Maya preferences folder
    try:
        # Install all required scripts
        for script in SCRIPT_LIST:
            install_script(script)
        
        # if OS_TYPE == "Mac": shutil.copy(SETUP_FILE, os.path.join(MAYA_SCRIPT_FOLDER, SHELF_SCRIPT))
        # VERSION_FILE = os.path.join(MAYA_SCRIPT_FOLDER, "VERSION")
        # if os.path.isfile(VERSION_FILE): os.remove(VERSION_FILE)

        return "All shelves and scripts installed successfully!\n\nThis window will close shortly..."
    
    # Print out errors
    except IOError as e: return "I/O Error:\n" + str(e)


##############################################################################################

# PLAT: Returns a string of platform type, e.g. "Windows"
PLAT = str(platform.system())



if "Darwin" in PLAT:
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

# MAYA_SCRIPT_FOLDER: e.g. C:/Users/hongj/Documents/maya/2020/scripts/
MAYA_SCRIPT_FOLDER = "{0}{1}/scripts/".format(MAYA_FOLDER,MAYA_VERSION)

# ANIMKIT_SCRIPT_FOLDER (aka the folder this script is located): e.g. c:\Users\hongj\Documents\GitHub\AnimKit\animkit
ANIMKIT_SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__)) 


# SETUP_FILE = os.path.join(ANIMKIT_SCRIPT_FOLDER, "\scripts\\", SHELF_SCRIPT)
SETUP_FILE = ANIMKIT_SCRIPT_FOLDER + "\scripts\\animkit_shelf.py"
    
# SCRIPT_LIST: A list of scripts to be installed.
SCRIPT_LIST = ["animkit_shelf.py", "animkit_basic.py", "animkit_playblast.py"]

# Main Setup
if os.path.isfile(SETUP_FILE): 
    print("AnimKit shelf install script is found. Begin installation.")
    print(install_shelf())
else: print("Unable to install AnimKit shelf.")

time.sleep(3.5)