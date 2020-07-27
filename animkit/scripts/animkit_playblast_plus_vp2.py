# Import Statement
from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
from subprocess import check_output, STDOUT, CalledProcessError
import os, time, getpass, shutil, subprocess, sys

# Version Info
version = "2.1.0"
update = "July 23, 2020"
new = "Fixed a bug in playblasting with padding."

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

    # Animation Start
    @property
    def START(self):
        return playbackOptions(q=1, animationStartTime=1)
        
    # Animation End
    @property
    def END(self):
        return playbackOptions(q=1, animationEndTime=1)
        
    # Playback Start
    @property
    def INNER_START(self):
        return playbackOptions(q=1, minTime=1)
        
    # Playback End
    @property
    def INNER_END(self):
        return playbackOptions(q=1, maxTime=1)
        

def getShotInfoStr():
    '''
    Get information about the currently open shot.
    '''

    comps = []
    
    # Shot Name
    shotName, extension = os.path.splitext(os.path.basename(cmds.file(q=True, sn=True)))
    comps.append('Shot: ' + str(shotName))

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

# Initial SSAO and MSAA state.
MSAA_STATE = cmds.getAttr('hardwareRenderingGlobals.multiSampleEnable')  # It's actually a Boolean
SSAO_STATE = cmds.getAttr('hardwareRenderingGlobals.ssaoEnable')
          
def set_ssao(reset = False):
    '''
    Screen Space Ambient Occlusion (SSAO) and Multi Sampling Anti Aliasing (MSAA).
    '''
    if not reset:
        mel.eval("setAttr hardwareRenderingGlobals.multiSampleEnable 1;")  # Anti-Aliasing in Viewport 2.0 
        mel.eval("setAttr hardwareRenderingGlobals.ssaoEnable 1;")  # Ambient Occlusion
    else:
        mel.eval("setAttr hardwareRenderingGlobals.multiSampleEnable " + str(int(MSAA_STATE)) + ";")  # Anti-Aliasing in Viewport 2.0 
        mel.eval("setAttr hardwareRenderingGlobals.ssaoEnable " + str(int(SSAO_STATE)) + ";")  # Ambient Occlusion

def quick_playblast(    width = None, # Use render width
                        height = None, # Use render height
                        startTime = TIMELINE.INNER_START, # Start frame of the playblast
                        endTime = TIMELINE.INNER_END, # End frame of the playblast
                        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE, # Args applied to the viewport to show/hide certain types of scene elements
                        outputNameAppend = "", # String appended to the output file name
                        showOrnaments = False, # Hide display elements from the playblast
                        usingTempFile = False, # Playblast temporarily to the default project path
                        convertH264 = False, # Encode the playblast into MP4, not AVI.
                        newName = "" # For iter++ to rename file name 
                    ):
    '''
    Provides a means of quality playblasting from an arbitary camera.
    '''
    
    # Error Message placeholder.
    errText = None

    print("[Playblast+] Will playblast from frame " + str(startTime) + " to frame " + str(endTime) + " .")

    # Render cam name.
    possibleRenderCams = ls("render_cam")
    
    if not len(possibleRenderCams) > 0: 
        return '\nNo camera in the scene\nnamed "render_cam".\n'

    if len(possibleRenderCams) > 1: 
        print('[Playblast+] WARNING: Multiple objects named render cam. Using the first one.')
    
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

    # Turn on SSAO and Anti-Aliasing
    set_ssao()

    # Playblast
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
            print("[Playblast+] Deleted PlayblastWindow")
        
        windowTitle = "Playblast Window"
        pbWin = window("PlayblastWindow", t = windowTitle)
        
        form = formLayout()
        description = text("This scene is now being playblasted and will close automatically when finished.", align="left")
        playblastpane = paneLayout(width=pbWidth, height=pbHeight)
        mp = modelPanel()
        
        # Choose Viewport
        cmds.modelEditor(mp, e=1, rnm="vp2Renderer") 
        
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
        mel.eval('lookThroughModelPanel ' + rc + " " + mp + ";")
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

            # For iter++ to override name
            if(newName != ""):
                pb_basename = newName
                print("[Playblast+] iter++ override name: " + newName)
            
            print("[Playblast+] new pb_base_name: " + pb_basename)

            pb_path = os.path.join(current_dir, pb_basename + outputNameAppend).replace('\\', '/')
            

            # Create /temp/ folder if do mp4 converting.
            if convertH264: 
                print("[Playblast+] Will convert final playblast into MP4.")
                pb_final_path = (current_dir +  "/temp/" + pb_basename + outputNameAppend).replace('\\', '/')
            else: 
                pb_final_path = pb_path.replace('\\', '/')
                
            print("[Playblast+] Playblast Location: " + pb_final_path)

            # Line of code that does the actual playblasting
            pb_actual_path = playblast(     filename = pb_final_path,
                                            format = "avi",
                                            forceOverwrite = True,
                                            offScreen = False,
                                            sequenceTime = 0,
                                            clearCache = 1,
                                            viewer = False,
                                            showOrnaments = showOrnaments,
                                            framePadding = 0,
                                            compression = "iyuv",
                                            quality = 100,
                                            percent = 100,
                                            width = pbWidth,
                                            height = pbHeight,
                                            useTraxSounds  = True,
                                            startTime = startTime,
                                            endTime = endTime  )
            
            # Code for playblasting into MP4.
            if convertH264:
                # Playblast AVI into a /temp/ folder.
                avi_input = (pb_actual_path + ".avi")
                mp4_output = (pb_actual_path + ".mp4")
                print("[Playblast+] avi_input: " + avi_input)
                print("[Playblast+] mp4_output: " + mp4_output)

                # Convert into MP4
                print("[Playblast+] Will Start to Convert to MP4. ")
                subprocess.call(["ffmpeg", "-y", "-i", avi_input, "-max_muxing_queue_size", "4096", mp4_output], shell=True)
                print("[Playblast+] Finished ffmpeg mp4 encoding.")
                
                # move it to playblast directory
                mp4_target_location = (mp4_output.replace("\\temp", ""))
                print("[Playblast+] mp4_target_location: " + mp4_target_location)
                print("[Playblast+] Debug: mp4_output exists: " + str(os.path.exists(mp4_output)))
                shutil.copyfile(mp4_output, mp4_target_location)
                print("[Playblast+] Successfully copied the MP4 output to: " + mp4_target_location)

                # Get rid of that /temp/ folder. 
                temp_folder_location = (current_dir +  "/temp/").replace('\\', '/')
                print("[Playblast+] TEMP folder location: " + temp_folder_location)
                shutil.rmtree(temp_folder_location)
                print("[Playblast+] Successfully recursively removed TEMP folder and its contents.")


            print("[Playblast+] Playblast successful!")
        except:
            errText = "\nAnimKit - Playblast Failed!! \n\n This could mean one of a few things:\n\n"+ \
            "1) Your previous playblast file is open.\n\n"+ \
            "2) Another copy of Maya is open.\n\n"+ \
            "3) There are  other things this script doesn't\naccount for.\n"
        pbWin.delete()
    except:
        errText = "\nThere was an issue creating a new window to do the playblast in, just playblast manually."
    
    # RESTORE STATE AND SHOW ANIMS
    ###############################
    mel.eval( 'camera -e -displayFilmGate off -displayResolution on -overscan 1.3 ' + rc + ';' )
    if (len(anim_shapes) > 0): showHidden( anim_shapes )
    if (len(selected) > 0): select( selected )
    set_ssao(reset=True)
    ###############################
    
    return errText


# save_file: Takes in a string of "filepath" and save the current file into the "filepath".
def save_file(filepath):
    cmds.file(rename = filepath)
    cmds.file(save = True, type = "mayaAscii") 

# general_playblast: A more general method that children methods can inherit most of its settings.
def general_playblast(startTime, # Start frame of the playblast
                        endTime, # End frame of the playblast
                        convert_h264 = False, 
                        append_text="", 
                        newNameGeneral=""):
    hudState = HeadsUpDisplayState.CURRENT()
    HeadsUpDisplayState.NONE().set()
    addHeadsUpShotInfo()

    # Some settings to be passed into playblast code
    result = quick_playblast(
        startTime = startTime, 
        endTime = endTime,
        viewportArgsSequence = DEFAULT_VIEWPORT_ARGS_SEQUENCE,
        outputNameAppend = append_text,
        showOrnaments = True,
        convertH264=convert_h264,
        newName = newNameGeneral
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
# Built in functions of Playblasting

# Viewport 2.0
# Viewport 2.0 Playblasting into AVI
def vp2_avi_playblast_nopadding(self):
    general_playblast(startTime = TimelineProperties().INNER_START, endTime = TimelineProperties().INNER_END, append_text="_nopadding")

def vp2_avi_playblast_padding(self):
    general_playblast(startTime = TimelineProperties().START, endTime = TimelineProperties().END, append_text="_w_padding")

# Viewport 2.0 Playblasting into MP4
def vp2_mp4_playblast_nopadding(self):
    general_playblast(startTime=TimelineProperties().INNER_START, endTime = TimelineProperties().INNER_END, convert_h264=True, append_text="_nopadding")

def vp2_mp4_playblast_padding(self):
    general_playblast(startTime=TimelineProperties().START, endTime = TimelineProperties().END, convert_h264=True, append_text="_w_padding")

#########################################################################################
# API

# Viewport 2.0 Playblasting into MP4 for i++
def vp2_mp4_playblast_ipp_nopadding(new_name):
    general_playblast(startTime=TimelineProperties().INNER_START, endTime = TimelineProperties().INNER_END, convert_h264=True, append_text="_nopadding", newNameGeneral=new_name)

def vp2_mp4_playblast_ipp_padding(new_name):
    general_playblast(startTime=TimelineProperties().START, endTime = TimelineProperties().END, convert_h264=True, append_text="_w_padding", newNameGeneral=new_name)