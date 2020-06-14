import sys, os, platform, shutil, glob
from pymel.core import *
import maya.cmds as cmds
import maya.utils as mayautils
import maya.mel as mel
import time as time

def get_latest_version(MAYA_FOLDER):
    version_folders = []
    for x in os.listdir(MAYA_FOLDER):
        try:
            folder = int(x)
            version_folders += [folder]
        except: pass
    return str(max(version_folders))

######## PRODUCTION SPECIFIC CONSTANTS ########
PLAT = str(platform.system())

if "Darwin" in PLAT:
    OS_TYPE = "Mac"
    USER = os.environ["HOME"]
    MAYA_FOLDER = "{0}/Library/Preferences/Autodesk/maya/".format(USER)
    DESKTOP = os.path.expanduser("~/Desktop")
else:
    OS_TYPE = "Windows"
    USER = os.getenv("USERPROFILE").replace('\\','/')
    MAYA_FOLDER = "{0}/Documents/maya/".format(USER)
    DESKTOP = USER + '/Desktop'

MAYA_VERSION = get_latest_version(MAYA_FOLDER)
CAPSTONE_SCRIPT_FOLDER = DESKTOP + "/capstone_scripts/"

# Paths to this year's meta rigging script modules (no environment variables necessary)
MODULE_PATHS = [CAPSTONE_SCRIPT_FOLDER]

# Path to the capstone shelf files on the network
NETWORK_PATH = (DESKTOP + "/capstone_scripts/capstone_shelves/").replace("/","\\")
             
###############################################
'''
Primary run method.
'''
def run(MAYA_VERSION, NETWORK_PATH):

    '''
    Update shelves
    '''
    oprint("=== ANIMATION CAPSTONE WORKSPACE STATUS =======================")
    oprint("")
    if os.path.isdir(NETWORK_PATH): oprint(update_capstone_shelves(MAYA_VERSION, NETWORK_PATH))
    else: oprint("Unable to update Animation Capstone shelves:  The network is unavailable or the shelves have been moved.")
    oprint("")
    oprint("===============================================================")
    oprint("")

    '''
    Set up miscellaneous Maya workspace options
    '''
    mel.eval('optionVar -iv "FileDialogStyle" 1') # Force OS native file dialog
    
    '''
    Execute this code after the scene startup
    '''
    mayautils.executeDeferred(setupMarkingMenus)
    mayautils.executeDeferred(removeKeyboardFolder)
    
'''
Set up marking menus.

Code must run AFTER Maya scene is loaded.
'''
def setupMarkingMenus():

    '''
    Creates hotkey set for animation capstone related hotkeys.
    This is a new requirement in Maya 2016, since the default
    hotkey set cannot be edited.
    '''
    
    CAPSTONE_HOTKEY_SET = 'AnimCapstoneHotkeys'

    # Create animation capstone hotkey set
    if not cmds.hotkeySet(CAPSTONE_HOTKEY_SET, q=1, ex=1): cmds.hotkeySet(CAPSTONE_HOTKEY_SET)

    # Set animation capstone hotkey set to current
    if cmds.hotkeySet(q=1, cu=1) != CAPSTONE_HOTKEY_SET: cmds.hotkeySet(CAPSTONE_HOTKEY_SET, e=1, cu=1)
    
    '''
    Set up marking menu
    '''

    # Marking menu commands
    cmds.nameCommand( 'mmm', annotation='Metacore Marking Menu', command = 'python("import gui; reload(gui); gui.MetaMarkingMenu()")')
    cmds.nameCommand( 'mmm_release', annotation='Metacore Marking Menu Release', command = 'python("import gui; reload(gui); gui.delete_metacore_marking_menu()")')
    cmds.nameCommand( 'quick_align', annotation='Metacore Quick Align', command = 'python("import gui; reload(gui); gui.quick_align()")')
    '''
    Setup hotkeys
    '''
    cmds.hotkey( k='A', ctl=True, name='mmm')
    cmds.hotkey( k='A', ctl=True, releaseName='mmm_release')
    cmds.hotkey( k='W', ctl=True,sht = True,name='quick_align')

    
'''
Maya has this small annoyance from 2013 where it creates a folder
called 'Keyboard' every time you boot up a file.  This attempts to pre-empt
that and automatically clean the production hierarchy as we go.

Code must run AFTER Maya scene is loaded.
'''
def removeKeyboardFolder():
    try:
        sceneDir = os.path.dirname(sceneName())
        potentialKeyboardFolder = os.path.join(sceneDir, "Keyboard")
        if (os.path.exists(potentialKeyboardFolder) and os.path.isdir(potentialKeyboardFolder)): os.rmdir(potentialKeyboardFolder)
    except:
        """ Fail silently... """

def oprint(str):
    sys.__stdout__.write(str+"\n")

def copy_files(src, dst):
    for fp in glob.glob(src):
        try: shutil.copy(fp, dst)
        except IOError as e: print e
            
def update_capstone_shelves(mayaVersion, networkPath):
    mayaPath1 = (MAYA_FOLDER + mayaVersion + '/').replace('/','\\')

    if not os.path.isdir(mayaPath1) and not os.path.isdir(mayaPath2) and not os.path.isdir(mayaPath3) and not os.path.isdir(mayaPath4) and not os.path.isdir(mayaPath5) and not os.path.isdir(mayaPath6) and not os.path.isdir(mayaPath7) and not os.path.isdir(mayaPath8) and not os.path.isdir(mayaPath9) and not os.path.isdir(mayaPath10):
        return "Default Maya folder not found."
    pathsToCheck = [mayaPath1]
    
    for mayaPath in pathsToCheck:
    
        localIcons = os.path.join(mayaPath, "prefs", "icons")
        localScripts = os.path.join(mayaPath, "scripts")
        localShelves = os.path.join(mayaPath, "prefs", "shelves")
        
        if not os.path.isdir(localIcons) or not os.path.isdir(localScripts) or not os.path.isdir(localShelves): continue
            
        # Copy over files
        oprint('UPDATING ICONS...')
        networkIcons = os.path.join(networkPath, "icons")+"\\*"
        copy_files(networkIcons, localIcons)
        oprint('UPDATING SCRIPTS...')
        networkScripts = os.path.join(networkPath, "scripts")+"\\*"
        copy_files(networkScripts, localScripts)
        oprint('UPDATING SHELVES...')
        networkShelves = os.path.join(networkPath, "shelves")+"\\*"
        copy_files(networkShelves, localShelves)
        
    # Finished successfully!
    return "\nShelves updated successfully!"

def check_for_updates(networkPath):
    localVersionPath = os.path.join(cmds.internalVar(usd=True), "VERSION")
    networkVersionPath = os.path.join(networkPath, "scripts", "VERSION")
    try:
        if (not os.path.exists(localVersionPath)): return True
        
        # Local version
        lvf = open(localVersionPath, "r")
        lv = int(lvf.readline())
        lvf.close()
        
        # Network version
        nvf = open(networkVersionPath, "r")
        nv = int(nvf.readline())
        nvf.close()
        
        # If the local version is less than the network version then updates are available
        if(lv < nv): return True
        else: return False
    except IOError as e: print e
    return False
    
'''
Setup and load general modules
'''
for mp in MODULE_PATHS:
    if not mp in sys.path: sys.path.append(mp)
    
'''
Run capstone workspace setup
'''
run(MAYA_VERSION, NETWORK_PATH)

## -- Add custom user setup commands below this line -- ##