##############################################################################################

# install_animkit.py
# Installs animkit shelf and its required files into the newest version of maya's /scripts folder.

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

# filter_ext: filters out files in a directory with the same extention and returns a list of filenames that contains the list of filenames.
def filter_ext (directory, ext):
    file_list = []
    for basename in os.listdir(directory):
        if basename.endswith(ext):
            file_list.append(basename)
    return file_list

# install_element: helper function for install_script, install_icon, etc. 
def install_element(element_name, target_folder, category):
    target_path = os.path.join(MAYA_SCRIPT_FOLDER, element_name)
    setup_file = ANIMKIT_FOLDER + target_folder + element_name
    shutil.copy(setup_file, target_path)
    print(category + " Copied " + element_name + " into: " + target_path)

# install_script: helper function for install_shelf. Installs a script into maya's .\scripts folder.
def install_script(script_name):
    install_element(script_name, "\scripts\\", "[SCRIPT]")
    
# install_icon: helper function for install_shelf. Installs a script into maya's .\scripts folder.
def install_icon(icon_name):
    install_element(icon_name, "\icons\\", "[ ICON ]")
    
# chk_dir: Checks if the given directory exists, if not, create one.
def chk_dir(target):
    if not os.path.isdir(target): 
        os.makedirs(target)
        print("[CHKDIR] Folder does not exist. Created script folder under: ", target)
    if os.path.isdir(MAYA_SCRIPT_FOLDER):
        print("[CHKDIR] Folder already exists under: ", target)

# install_shelf:
# Installs all required elements.
def install_shelf():
    # Check if the Maya script folder exists, if not, create one.
    chk_dir(MAYA_SCRIPT_FOLDER)
    chk_dir(MAYA_ICON_FOLDER)

    # Copy setup file into the Maya preferences folder
    try:
        # Install all required elements
        for script in SCRIPT_LIST: install_script(script)
        for icon in ICON_LIST: install_icon(icon)
        return "[FINISH] All required files installed successfully!"
    
    # Print out errors
    except IOError as e: return "[FINISH] I/O Error:\n" + str(e)


##############################################################################################

# PLAT: Returns a string of platform type, e.g. "Windows"
PLAT = str(platform.system())


# Define OS type, Legacy.
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

# MAYA_SCRIPT_FOLDER: Where maya stores all its scripts
MAYA_SCRIPT_FOLDER = "{0}{1}/scripts/".format(MAYA_FOLDER,MAYA_VERSION)

# MAYA_ICON_FOLDER: Create a /animkit/ folder in the Maya icon folder
MAYA_ICON_FOLDER = "{0}{1}/prefs/icons/animkit/".format(MAYA_FOLDER,MAYA_VERSION)

# ANIMKIT_FOLDER: aka the folder this script is located
ANIMKIT_FOLDER = os.path.dirname(os.path.abspath(__file__)) 

# SETUP_FILE = The shelf itself.
SETUP_FILE = ANIMKIT_FOLDER + "\scripts\\animkit_shelf.py"
    
# SCRIPT_LIST: A list of str of scripts in /scripts folder.
SCRIPT_LIST = filter_ext(ANIMKIT_FOLDER + "\scripts", ".py")

# ICON_LIST: A list of str of icons in /icons folder.
ICON_LIST = filter_ext(ANIMKIT_FOLDER + "\icons", ".png")

# Main Setup.
if os.path.isfile(SETUP_FILE): 
    print("[ BOOT ] AnimKit shelf install script is found. Begin installation.")
    print(install_shelf())
else: print("[ BOOT ] Cannot find the animkit shelf file.")

time.sleep(3.5)