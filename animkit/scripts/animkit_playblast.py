from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import os
import time
import getpass
import shutil
import subprocess,sys

##############################################################################################

# Install required packages

# install: Install a package by calling sys and pip.
# Takes in a str package and calls "pip install package". 
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    msg = package + "successfully installed."
    cmds.confirmDialog(title='Package Installed Successfully', message=msg, button=['Anim!'], defaultButton='Anim!', dismissString='Anim!')


def install_ffmpeg(self):
    install("ffmpeg-python")  # ffmpeg is required to make playblast to mp4 work


##############################################################################################


# Default sequence of enabling/disabling viewport elements
DEFAULT_VIEWPORT_ARGS_SEQUENCE = [  ("displayAppearance" , "smoothShaded"),
                                    ("displayTextures" , True),
                                    ("displayLights" , "default"),
                                    ("allObjects" , False),
                                    ("grid" , False),
                                    ("polymeshes" , True),
                                    ("nurbsSurfaces" , True),
                                    ("fluids" , True),
                                    ("dynamics" , True) ]

class HeadsUpDisplayState:
    
    @staticmethod
    def CURRENT():
        '''
        Get current heads up display state.
        '''
        stateTable = {}
        for e in headsUpDisplay(lh=True):
            isVisible = headsUpDisplay(e, vis=1, q=1)
            stateTable[e] = isVisible
        return HeadsUpDisplayState(stateTable)
    
    def __init__(self, stateTable):
        self._stateTable = stateTable
    
    @staticmethod
    def NONE():
        '''
        Get state of heads up display when everything is disabled.
        '''
        stateTable = {}
        for e in headsUpDisplay(lh=True):
            stateTable[e] = False
        return HeadsUpDisplayState(stateTable)
    
    def printState(self):
        '''
        Print state.
        '''
        for e, v in self._stateTable.iteritems():
            print str(e) + " = " + str(v)
            
    def set(self):
        '''
        Set heads up display to this current state.
        '''
        
        for e in headsUpDisplay(lh=True):
            headsUpDisplay(e, vis=False, e=1) # Hidden by default (so new elements are accounted for)
            if e in self._stateTable:
                headsUpDisplay(e, vis=self._stateTable[e], e=1)

                
class TimelineProperties:

    @property
    def START(self):
        return playbackOptions(q=1, animationStartTime=1)
        
    @property
    def END(self):
        return playbackOptions(q=1, animationEndTime=1)
        
    @property
    def INNER_START(self):
        return playbackOptions(q=1, minTime=1)
        
    @property
    def INNER_END(self):
        return playbackOptions(q=1, maxTime=1)
        

def getShotInfoStr():
    '''
    Get information about the currently open shot.
    '''

    comps = []

    '''
    # If this scene name isn't saved then skip
    if sceneName() == '': return 'Unsaved Scene'

    # If this is in the shot folder include the sequence and shot number
    path = sceneName().replace('\\', '/')
    if ('production/assets/shot/' in path):
        splitPath = path.split('production/assets/shot/')
        shotFolder = splitPath[-1].split('/')[0]
        formattedName = shotFolder.replace('_', ' ').upper()
        comps.append(formattedName)
    
    # Query username
    userName = getpass.getuser()
    if userName in USERNAME_TO_NAME:
        userName = USERNAME_TO_NAME[userName]
    comps.append(userName)
    '''
    
    # Last modified time
    lastModified = time.ctime(os.path.getmtime(sceneName()))
    lastModified = lastModified.split(' ')[1:-1]
    lastModified = ' '.join(lastModified)
    comps.append('Updated on '+str(lastModified))
    
    '''
    # Frame number
    frameNumber = str(int(currentTime()))
    comps.append(frameNumber)
    '''

    return '   |   '.join(comps)


def addHeadsUpShotInfo():
    '''
    Add shot information heads up display element.
    '''
    
    if headsUpDisplay("HUDShotInfo", exists=1):
        headsUpDisplay("HUDShotInfo", rem=1)
    headsUpDisplay(     rp=[5,0]     )
    headsUpDisplay(     "HUDShotInfo",
                        section=5,
                        block=0,
                        blockSize="large",
                        blockAlignment="left",
                        dfs="large",
                        ao=1,
                        command=getShotInfoStr,
                        atr=True    )
    headsUpDisplay("HUDShotInfo", vis=True, e=1)
    
    
def removeHeadsUpShotInfo():
    '''
    Remove heads up display shot information if it exists.
    '''
    
    if headsUpDisplay("HUDShotInfo", exists=1):
        headsUpDisplay("HUDShotInfo", rem=1)
        
    
TIMELINE = TimelineProperties()
          
          
def quick_playblast(    renderCamName = "render_cam",
                        format = "avi",
                        compression = "iyuv",
                        quality = 70,
                        width = None, # Use render width
                        height = None, # Use render height
                        startTime = TIMELINE.INNER_START, # Start frame of the playblast
                        endTime = TIMELINE.INNER_END, # End frame of the playblast
                        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE, # Args applied to the viewport to show/hide certain types of scene elements
                        outputNameAppend = "", # String appended to the output file name
                        showOrnaments = False, # Hide display elements from the playblast
                        usingTempFile = False # Playblast temporarily to the default project path
                    ):
    '''
    Provides a means of quality playblasting from an arbitary camera.
    '''
    
    errText = None

    # Render cam name
    possibleRenderCams = ls(renderCamName)
    
    if not len(possibleRenderCams) > 0: return '\nNo camera in the scene\nnamed "render_cam".\n'

    if len(possibleRenderCams) > 1: print 'WARNING: Multiple objects named render cam. Using the first one.'
    
    rc = possibleRenderCams[0].fullPath()
    
    if type(PyNode(rc).getShape()) != nt.Camera: return '\nObject named "render_cam" isn\'t actually a camera.'

    # SAVE STATE AND HIDE ANIMS
    ############################
    mel.eval( 'camera -e -displayFilmGate off -displayResolution off -overscan 1.0 ' + rc + ';' )
    # Deselect selected objects
    selected = ls(sl=1)
    if (len(selected) > 0): select(selected, d=1)
    # Hide anim shapes
    anims = ls("*_topCon", r=1) + ls("*_anim*", r=1, typ="joint") + ls("*_anim*", r=1, typ="mesh")
    if len(anims) > 0: anim_shapes = listRelatives(anims, s=1, f=1)
    else: anim_shapes = []
    anim_shapes =  filter(lambda sh: getAttr(sh+".visibility") > 0, anim_shapes) # filter out unselected shapes
    if (len(anim_shapes) > 0): hide(anim_shapes)
    ############################

    try:
        try: res = PyNode("defaultResolution")
        except: res = None
    
        # Set playblast width
        if (width != None):     pbWidth = int(width)
        elif (res != None):     pbWidth = int(res.width.get())
        else:                   pbWidth = 640
                
        # Set playblast height
        if (height != None):    pbHeight = int(height)
        elif (res != None):     pbHeight = int(res.height.get())
        else:                   pbHeight = 360

        # Create new window with model panel for playblasting
        if window("PlayblastWindow", q=1, exists=1):
            deleteUI("PlayblastWindow")
            print "deleted"
        windowTitle = "Window of Playblasting"
        pbWin = window("PlayblastWindow", t=windowTitle)
        
        form = formLayout()
        description = text("Your scene is now being playblasted using this window.  It will close automatically when finished.\nNote that for now it's actually rendering offscreen.", align="left")
        playblastpane = paneLayout(width=pbWidth, height=pbHeight)
        mp = modelPanel()
        
        # Force Viewport 2.0
        cmds.modelEditor(mp, e=1, rnm='vp2Renderer')
        
        # Attach controls to the layout
        form.attachForm(description, 'top', 5)
        form.attachForm(description, 'left', 5)
        form.attachForm(description, 'right', 5)
        form.attachControl(playblastpane, 'top', 5, description)
        form.attachForm(playblastpane, 'left', 5)
        form.attachForm(playblastpane, 'right', 5)
        form.attachForm(playblastpane, 'bottom', 5)
        
        # Playblast model panel options
        mp.setMenuBarVisible(False)
        ui.PyUI(layout(mp.getBarLayout(), q=1, ca=1)[0]).delete() # Remove icon bar
        setFocus(mp)
        mel.eval('lookThroughModelPanel '+rc+" "+mp);
        showWindow(pbWin)
        refresh()
        
        # Set up model panel for playblasting
        for vpArg in viewportArgsSequence:
            try:
                vpArgName = str(vpArg[0])
                vpArgValue = vpArg[1]
                
                if (isinstance(vpArgValue, str)):
                    vpArgValue = '"'+vpArgValue+'"'
                else:
                    vpArgValue = str(vpArgValue)

                vpCmd = 'modelEditor( mp, e=1, '+vpArgName+'='+vpArgValue+' )'
                eval(vpCmd)
            except:
                continue

        # Do playblast
        try:
            # Playblast file target path
            scene_path = cmds.file( location=True, query=True )
            current_dir = os.path.dirname( scene_path )
            basename = os.path.basename( scene_path )
            pb_basename = basename.split(".")[0]
            pb_path = os.path.join( current_dir, pb_basename+outputNameAppend ).replace( '\\', '/' )
            
            # Playblast file temp path
            # - Okay, so here's the deal.  Playblasting to the network using h264 is
            #   in simple terms, "hella broke".  So we're going to find a suitable
            #   local location to playblast to, then copy the resulting playblast to
            #   the network.
            temp_file_target_folder = os.getenv('MAYA_APP_DIR')
            
            if usingTempFile and os.path.exists(temp_file_target_folder):
                pb_temp_path = os.path.join(temp_file_target_folder, 'TEMP_MAYA_PLAYBLAST')
            else:
                pb_temp_path = pb_path
            
            # Line of code that does the actual playblasting
            pb_actual_path = playblast(     filename = pb_temp_path,
                                            format = format,
                                            forceOverwrite = True,
                                            offScreen = False,
                                            sequenceTime = 0,
                                            clearCache = 1,
                                            viewer = True,
                                            showOrnaments = showOrnaments,
                                            framePadding = 0,
                                            compression = compression,
                                            quality = quality,
                                            percent = 100,
                                            width = pbWidth,
                                            height = pbHeight,
                                            useTraxSounds  = True,
                                            startTime = startTime,
                                            endTime = endTime  )
            
            # Copy temp file over
            if usingTempFile:
                pb_extension = pb_actual_path.split('.')[-1]
                shutil.copyfile(pb_actual_path, pb_path+'.'+pb_extension)
                        
            print("Playblast SUCCESSFUL!")
        except:
            errText = "\nThis could mean one of a few things:\n\n"+ \
            "1) Your previous playblast file is open.  You will need to close\nQuicktime/VLC/Windows Media Player.\n\n"+ \
            "2) Another copy of Maya is open.\n\n"+ \
            "3) Somebody else in the lab has your playblast open...\n\n"+ \
            "4) There are network issues or other things this script doesn't\naccount for. If the error persists just do the playblast manually.\n"
        pbWin.delete()
    except:
        errText = "\nThere was an issue creating a new window to do the playblast in, just playblast manually and let the staff know."
    
    # RESTORE STATE AND SHOW ANIMS
    ###############################
    mel.eval( 'camera -e -displayFilmGate off -displayResolution on -overscan 1.3 ' + rc + ';' )
    if (len(anim_shapes) > 0): showHidden( anim_shapes )
    if (len(selected) > 0): select( selected )
    ###############################
    
    # We're done!
    return errText


def quick_playblast_cmd():
    '''
    One click playblast at the scene resolution.
    '''
    
    """
    OLD CODE DISABLED UNTIL ANIMATIC IS COMPLETE
    result = quick_playblast(
        width = None,
        height = None,
        startTime = TIMELINE.INNER_START, 
        endTime = TIMELINE.INNER_END,
        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE
    )
    
    quick_playblast_err(result)
    """
    

    hudState = HeadsUpDisplayState.CURRENT()
    HeadsUpDisplayState.NONE().set()
    addHeadsUpShotInfo()
    
    result = quick_playblast(
        width = 640,
        height = 360,
        startTime = TIMELINE.INNER_START, 
        endTime = TIMELINE.INNER_END,
        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE,
        showOrnaments = True,
        outputNameAppend = "_range"
    )
    
    removeHeadsUpShotInfo()
    hudState.set()
    quick_playblast_err(result)

    
def quick_playblast_motionmatic_cmd(self):
    '''
    One click playblast at 640x360 of the entire timeline.
    '''
    
    hudState = HeadsUpDisplayState.CURRENT()
    HeadsUpDisplayState.NONE().set()
    addHeadsUpShotInfo()

    result = quick_playblast(
        width = 640,
        height = 360,
        startTime = TIMELINE.START, 
        endTime = TIMELINE.END,
        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE,
        #outputNameAppend = "_playblast",
        showOrnaments = True
    )
    
    removeHeadsUpShotInfo()
    hudState.set()
    quick_playblast_err(result)

    
def quick_playblast_review_cmd():
    '''
    One click playblast at 640x360 of the entire timeline minus 24 frames of padding.
    '''
    
    result = quick_playblast(
        width = 640,
        height = 360,
        startTime = TIMELINE.START+24, 
        endTime = TIMELINE.END-24,
        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE,
        outputNameAppend = "_for_review"
    )
    quick_playblast_err(result)
    

def quick_playblast_err(errText):
    '''
    Prints error message of a playblast result, if any.
    '''

    # If an error occurred, print error message
    if errText is not None:
        errW = window(t="ERROR PLAYBLASTING!", w=100, h=100)
        columnLayout( adjustableColumn=True )
        text( label=errText, align="left")
        button( label='Okay', command=Callback(errW.delete) )
        showWindow(errW)
