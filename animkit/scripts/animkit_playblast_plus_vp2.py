# Import Statement
from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
from subprocess import check_output, STDOUT, CalledProcessError
import os, time, getpass, shutil, subprocess, sys


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
            print(str(e) + " = " + str(v))
            
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
    
    # Last modified time
    lastModified = time.ctime(os.path.getmtime(sceneName()))
    lastModified = lastModified.split(' ')[1:-1]
    lastModified = ' '.join(lastModified)
    comps.append('Updated Date: ' + str(lastModified))
    
    # Frame number
    frameNumber = str(int(currentTime()))
    comps.append('Frame: ' + frameNumber)

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
                        quality = 100,
                        width = None, # Use render width
                        height = None, # Use render height
                        startTime = TIMELINE.INNER_START, # Start frame of the playblast
                        endTime = TIMELINE.INNER_END, # End frame of the playblast
                        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE, # Args applied to the viewport to show/hide certain types of scene elements
                        outputNameAppend = "", # String appended to the output file name
                        showOrnaments = False, # Hide display elements from the playblast
                        usingTempFile = False, # Playblast temporarily to the default project path
                        convertH264 = False, # Encode the playblast into MP4, not AVI.
                        renderName = "vp2Renderer", # Not gonna implement Arnold in this :P Arnold is quite different!
                    ):
    '''
    Provides a means of quality playblasting from an arbitary camera.
    '''
    
    # Error Message placeholder.
    errText = None

    

    # Render cam name.
    possibleRenderCams = ls(renderCamName)
    
    if not len(possibleRenderCams) > 0: 
        return '\nNo camera in the scene\nnamed "render_cam".\n'

    if len(possibleRenderCams) > 1: 
        print('WARNING: Multiple objects named render cam. Using the first one.')
    
    rc = possibleRenderCams[0].fullPath()
    
    if type(PyNode(rc).getShape()) != nt.Camera: 
        return '\nObject named "render_cam" isn\'t actually a camera.'

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
        else:                   pbWidth = 1280
                
        # Set playblast height
        if (height != None):    pbHeight = int(height)
        elif (res != None):     pbHeight = int(res.height.get())
        else:                   pbHeight = 720

        # Create new window with model panel for playblasting
        # Is this really necessary...
        if window("PlayblastWindow", q=1, exists=1):
            deleteUI("PlayblastWindow")
            print("Deleted PlayblastWindow")
        windowTitle = "Window of Playblasting"
        pbWin = window("PlayblastWindow", t=windowTitle)
        
        form = formLayout()
        description = text("Your scene is now being playblasted using this window. It will close automatically when finished.\nNote that for now it's actually rendering offscreen.", align="left")
        playblastpane = paneLayout(width=pbWidth, height=pbHeight)
        mp = modelPanel()
        
        # Choose Viewport
        cmds.modelEditor(mp, e=1, rnm=renderName)  # Default Viewport 2.0, future might add in Arnold support
        
        print("ModelEditor", cmds.modelEditor(mp, query=True, rendererListUI=True))
        
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
            # Handle case if the file is not saved.
            if (cmds.file( location=True, query=True ) == "unknown"):
                filePath = str(cmds.fileDialog2(fileFilter="*.ma", dialogStyle=2, caption='Save As')[0])
                save_file(filePath)
                

            # Set Path of Playblast.
            scene_path = cmds.file(location=True, query=True) 
            current_dir = os.path.dirname(scene_path)
            basename = os.path.basename(scene_path)
            pb_basename = basename.split(".")[0]
            pb_path = os.path.join(current_dir, pb_basename + outputNameAppend).replace( '\\', '/' )
            

            # Create /temp/ folder if do mp4 converting.
            if convertH264: 
                pb_final_path = (current_dir +  "/temp/" + pb_basename + outputNameAppend).replace( '\\', '/' )
            else: 
                pb_final_path = pb_path
                

            # Line of code that does the actual playblasting
            pb_actual_path = playblast(     filename = pb_final_path,
                                            format = format,
                                            forceOverwrite = True,
                                            offScreen = False,
                                            sequenceTime = 0,
                                            clearCache = 1,
                                            viewer = False,
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
            
            # Actual code for playblasting into MP4.
            if convertH264:
                # Playblast AVI into a /temp/ folder.
                avi_input = pb_actual_path + ".avi"
                mp4_output = pb_actual_path + ".mp4"

                # Convert into MP4
                subprocess.call("ffmpeg -y -i {input} {output}".format(input = avi_input, output = mp4_output))
                
                # move it to playblast directory
                mp4_target_location = mp4_output.replace("\\temp", "")
                shutil.copyfile(mp4_output, mp4_target_location)

                # Get rid of that /temp/ folder. 
                temp_folder_location = current_dir +  "/temp/"
                shutil.rmtree(temp_folder_location)


            print("AnimKit - Playblast+: Playblast successful!")
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
    
    return errText


# save_file: Takes in a string of "filepath" and save the current file into the "filepath".
def save_file(filepath):
    cmds.file(rename=filepath)
    cmds.file(save=True, type="mayaAscii") 

# general_playblast: A more general method that children methods can inherit most of its settings.
def general_playblast(start_time, end_time, convert_h264=False, use_arnold=False, append_text=""):
    hudState = HeadsUpDisplayState.CURRENT()
    HeadsUpDisplayState.NONE().set()
    addHeadsUpShotInfo()

    # Some settings to be passed into playblast code
    result = quick_playblast(
        startTime = start_time, 
        endTime = end_time,
        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE,
        outputNameAppend = append_text,
        showOrnaments = True,
        convertH264=convert_h264,
    )

    removeHeadsUpShotInfo()
    hudState.set()

    # Handle error message
    if result is not None:
        errW = window(t="ERROR PLAYBLASTING!", w=100, h=100)
        columnLayout( adjustableColumn=True )
        text( label=result, align="left")
        button( label='Okay', command=Callback(errW.delete) )
        showWindow(errW)

#########################################################################################
# Different Options of Playblasting

# Viewport 2.0
# Viewport 2.0 Playblasting into AVI
def vp2_avi_playblast_nopadding(self):
    general_playblast(start_time=TIMELINE.START+24, end_time = TIMELINE.END-24, append_text="_nopadding")

def vp2_avi_playblast_padding(self):
    general_playblast(start_time=TIMELINE.START, end_time = TIMELINE.END, append_text="_w_padding")

# Viewport 2.0 Playblasting into MP4
def vp2_mp4_playblast_nopadding(self):
    general_playblast(start_time=TIMELINE.START+24, end_time = TIMELINE.END-24, convert_h264=True, append_text="_nopadding")

def vp2_mp4_playblast_padding(self):
    general_playblast(start_time=TIMELINE.START, end_time = TIMELINE.END, convert_h264=True, append_text="_w_padding")
