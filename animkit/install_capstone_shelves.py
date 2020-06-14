import time, os, platform, shutil

##############################################################################################
def get_latest_version(MAYA_FOLDER):
    version_folders = []
    for x in os.listdir(MAYA_FOLDER):
        try:
            folder = int(x)
            version_folders += [folder]
        except: pass
    return str(max(version_folders))

def install_shelf():
    if not os.path.isdir(MAYA_SCRIPT_FOLDER): os.makedirs(MAYA_SCRIPT_FOLDER)
            
    # Copy setup file into the Maya preferences folder
    if not os.path.isfile(SETUP_FILE): return "Cannot find shelf setup file on the network."
    try:
        shutil.copy(SETUP_FILE, os.path.join(MAYA_SCRIPT_FOLDER, PY_FILE))
        if OS_TYPE == "Mac": shutil.copy(SETUP_FILE, os.path.join(MAYA_SCRIPT_FOLDER, "userSetup.mel"))
        VERSION_FILE = os.path.join(MAYA_SCRIPT_FOLDER, "VERSION")
        if os.path.isfile(VERSION_FILE): os.remove(VERSION_FILE)
        return "Shelves installed successfully!\n\nThis window will close shortly..."
    except IOError as e: return "I/O Error:\n" + str(e)

##############################################################################################
PLAT = str(platform.system())
PY_FILE = "userSetup.py"

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
MAYA_SCRIPT_FOLDER = "{0}{1}/scripts/".format(MAYA_FOLDER,MAYA_VERSION)
CAPSTONE_SCRIPT_FOLDER = DESKTOP + "/capstone_scripts/capstone_shelves/scripts/"
SETUP_FILE = os.path.join(CAPSTONE_SCRIPT_FOLDER, PY_FILE)

# figure out what to do
if os.path.isdir(CAPSTONE_SCRIPT_FOLDER): print(install_shelf())
else: print("Unable to install Animation Capstone shelves, the network may be unavailable.")

time.sleep(3.5)