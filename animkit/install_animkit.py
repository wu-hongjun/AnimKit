##############################################################################################

# install_animkit.py
# Installs animkit shelf and its required files into the newest version of maya's /scripts folder.

##############################################################################################
# Import required packages

import time, os, platform, shutil, subprocess, sys
from datetime import datetime

# Info about this version of installer.
VERSION = "1.1.0"
BUILD = "20200717"

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
def install_element(element_name, target_folder, category, maya_path):
    target_path = os.path.join(maya_path, element_name)
    setup_file = ANIMKIT_FOLDER + target_folder + element_name
    shutil.copy(setup_file, target_path)
    print(category + " Installed " + element_name + " into: " + target_path)

# install_script: helper function for install_shelf. Installs a script into maya's .\scripts folder.
def install_script(script_name):
    install_element(script_name, "\scripts\\", "[✓] [SCRIPT]", MAYA_SCRIPT_FOLDER)

def install_plugin(plugin_name):
    install_element(plugin_name, "\plug-ins\\", "[✓] [PLUGIN]", MAYA_PLUGIN_FOLDER)
    
# install_icon: helper function for install_shelf. Installs a script into maya's .\scripts folder.
def install_icon(icon_name):
    install_element(icon_name, "\icons\\", "[✓] [ ICON ]", MAYA_ICON_FOLDER)
    
def install_extension():
    return True  # No extension yet for future scaling

# chk_dir: Checks if the given directory exists, if not, create one.
def chk_dir(folder, target):
    if not os.path.isdir(target): 
        os.makedirs(target)
        print("[⍻] [CHKDIR] " + folder + " folder does not exist. Created script folder under: ", target)
    if os.path.isdir(target):
        print("[✓] [CHKDIR] "+ folder + " folder already exists under: ", target)

# install_shelf:
# Installs all required elements.
def install_shelf():
    # Check if the Maya script folder exists, if not, create one.
    chk_dir("Script", MAYA_SCRIPT_FOLDER)
    chk_dir("Icon", MAYA_ICON_FOLDER)
    chk_dir("Plug-In", MAYA_PLUGIN_FOLDER)

    # Copy setup file into the Maya preferences folder
    try:
        # Install all required elements
        for script in SCRIPT_LIST: install_script(script)
        for icon in ICON_LIST: install_icon(icon)
        for plugin in PLUGIN_LIST: install_plugin(plugin)
        return "[✓] [FINISH] All required files installed successfully!"
    
    # Print out errors
    except IOError as e: return "[X] [FINISH] I/O Error:\n" + str(e)


##############################################################################################

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

# MAYA_PLUGIN_FOLDER: Where maya stores all its scripts
MAYA_PLUGIN_FOLDER = "{0}{1}/plug-ins/".format(MAYA_FOLDER,MAYA_VERSION)

# MAYA_ICON_FOLDER: Create a /animkit/ folder in the Maya icon folder
MAYA_ICON_FOLDER = "{0}{1}/prefs/icons/animkit/".format(MAYA_FOLDER,MAYA_VERSION)

# ANIMKIT_FOLDER: aka the folder this script is located
ANIMKIT_FOLDER = os.path.dirname(os.path.abspath(__file__)) 

# SETUP_FILE = The shelf itself.
SETUP_FILE = ANIMKIT_FOLDER + "\scripts\\animkit_shelf.py"
    
# SCRIPT_LIST: A list of str of scripts in /scripts folder.
PYTHON_LIST = filter_ext(ANIMKIT_FOLDER + "\scripts", ".py")
MEL_LIST = filter_ext(ANIMKIT_FOLDER + "\scripts", ".mel")
SCRIPT_LIST = PYTHON_LIST + MEL_LIST

# PLUGIN_LIST: List of plugins of ".mll" files
MLL_LIST = filter_ext(ANIMKIT_FOLDER + "\plug-ins", ".mll")
PLUGIN_LIST = MLL_LIST

# ICON_LIST: A list of str of icons in /icons folder.
PNG_LIST = filter_ext(ANIMKIT_FOLDER + "\icons", ".png")
JPG_LIST = filter_ext(ANIMKIT_FOLDER + "\icons", ".jpg")
ICON_LIST = PNG_LIST + JPG_LIST

# dd/mm/YY H:M:S
date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# Main Setup.
print("[✓] [WELCOM] Welcome to AnimKit Installer! This script will install AnimKit to the newest version of Maya.")
print("[✓] [WELCOM] AnimKit Installer Version: " + VERSION + " | Build: " + BUILD + " | Current Time: " + date_time)
if os.path.isfile(SETUP_FILE): 
    print("[✓] [ BOOT ] AnimKit shelf main script is found. Begin installation.")
    print(install_shelf())
else: print("[X] [ BOOT ] Cannot find the animkit shelf file.")

time.sleep(3.5)