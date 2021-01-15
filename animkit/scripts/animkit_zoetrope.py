from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import shutil, subprocess, sys, getpass, time, os, platform
from mtoa.cmds.arnoldRender import arnoldRender
from os import listdir
from os.path import isfile, join

# Version Info
VERSION = "2.2.0"
UPDATE = "Aug 26, 2020"
NEW = "Zoetrope 2.2 brings bug fixes as well as new features like automatic padding detection, frame range prompt, etc."


# =================================================== Maya Elements ===================================================
# Current Timeline
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

# Getter Methods
def get_resolution_settings(attr):
    '''
    attr = "width" or "height".
    Returns an int of the current width or height of the current render settings.
    '''
    return cmds.getAttr("%s.%s"%("defaultResolution", attr))

def get_padding():
    '''
    Returns an int of the current frame padding in the render settings.
    '''
    return cmds.getAttr("defaultRenderGlobals.extensionPadding")

def get_frame_rate():
    '''
    Returns an int of the framerate of the current scene.
    '''
    # Framerate Info
    FRAMERATE_INFO = {"game":15, "film":24, "pal":25, "ntsc":30, "show":48, "palf":50, "ntscf":60}
    current_time = cmds.currentUnit(query=True, time=True)
    return FRAMERATE_INFO.get(current_time)

def toggle_render_settings():
    # Mainly, this should set the render setting to name_#.ext so stuff can move forward.

    # This controls the "_" in the padding, 0 for nothing, 1 for ".", and 2 for "_".
    cmds.setAttr("defaultRenderGlobals.periodInExt", 2)  
    
    # This controls the "ext". Setting this to 0 makes name_#.ext while 1 makes name.#
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)  

    # This controls whether you want to render a single frame. 0 for single frame, and 1 for the animation.
    cmds.setAttr("defaultRenderGlobals.animation", 1)

    # This controls whether you want the extension or the frame number to go first in the file name.
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)

    # This controls whether you want the extension ".ext" to be in your image name at all.
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    print("[Zoetrope] Set Padding - Render settings correctly set.")

# =================================================== Arnold Driver Global Setting ===================================================
# An attempt to fix the global render path location problem
global DEFAULTARNOLDDRIVER_PRE
DEFAULTARNOLDDRIVER_PRE = ""

def cache_defaultArnoldDriver_pre():
    '''
    Returns an string of the defaultArnoldDriver.pre
    '''
    global DEFAULTARNOLDDRIVER_PRE
    DEFAULTARNOLDDRIVER_PRE = cmds.getAttr("defaultArnoldDriver.pre")
    print("[Zoetrope] Arnold Driver Global Setting - Successfully get and cached defaultArnoldDriver.pre settings: " + DEFAULTARNOLDDRIVER_PRE)

def set_defaultArnoldDriver_pre():
    '''
    Sets the defaultArnoldDriver.pre to its original state.
    '''
    cmds.setAttr("defaultArnoldDriver.pre", DEFAULTARNOLDDRIVER_PRE, type="string")
    print("[Zoetrope] Arnold Driver Global Setting - Successfully reset defaultArnoldDriver.pre settings to original: " + DEFAULTARNOLDDRIVER_PRE)

def fix_defaultArnoldDriver_pre(self):
    '''
    Sets the defaultArnoldDriver.pre to its original state of "".
    '''
    cmds.setAttr("defaultArnoldDriver.pre", "", type="string")
    print("[Zoetrope] Arnold Driver Global Setting - Successfully fixed defaultArnoldDriver.pre settings to original.")
# =================================================== Zoetrope Renderer ===================================================
# Render Functions
def render_frame(width, height, frame, file_format="tif", render_layer = "defaultRenderLayer", image_padding = get_padding()):
    '''
    HELPER for batch_render().
    Render the selected frame into scene_folder/renders/render_layer/ folder.
    '''
    # ====================================== Cache defaultArnoldDriver.pre ======================================
    frame = int(frame)
    print("[Zoetrope] Frame Renderer - Currently rendering frame " + str(frame) + " .")
    cache_defaultArnoldDriver_pre()

    # ====================================== Render the frame ======================================
    file_dir = (sceneName().parent + "\\renders\\" + render_layer).replace('\\', '/')
    prepend = os.path.basename(sceneName()).split('.')[0]
    cmds.setAttr("defaultArnoldDriver.ai_translator", file_format, type="string")
    cmds.setAttr("defaultArnoldDriver.pre", file_dir + "\\" + prepend, type="string")
    cmds.setAttr("render_camShape.mask", 1)
    arnoldRender(width, height, True, True,'render_cam', ' -layer ' + render_layer)

    # ====================================== Fix the weird _1_ bug ======================================
    # Known bug: The result file generated by arnoldRender() adds a _1_ to the file name
    bug = "_1_"  # idk whyyyy does this happen 
    prefix_image_dir = file_dir + "\\" + prepend + bug + "{:0>4d}".format(frame) + "." + file_format
    postfix_image_dir = file_dir + "\\" + prepend + "_" + "{:0>4d}".format(frame) + "." + file_format
    # print("[Zoetrope] Frame Renderer - Prefix Image Directory: " + prefix_image_dir)  # Debug
    # print("[Zoetrope] Frame Renderer - Postfix Image Directory: " + postfix_image_dir)  # Debug
    
    if os.path.exists(postfix_image_dir): 
        os.remove(postfix_image_dir)
        if not os.path.exists(postfix_image_dir):
            print("[Zoetrope] Frame Renderer - Image exists at: " + postfix_image_dir + " and got deleted successfully.")

    os.rename(prefix_image_dir,postfix_image_dir)

    # ====================================== Reset defaultArnoldDriver.pre ======================================
    set_defaultArnoldDriver_pre()
    


def batch_render(renderStart, renderEnd, width = get_resolution_settings("width"), height = get_resolution_settings("height"), target_format = "tif", useDefaultRenderLayer = False):
    '''
    Calls render_frame and perform batch rendering.
    '''
    # ====================================== Prompt user to check render range. ======================================
    msg = "Will render from frame " + str(renderStart) + " to frame " + str(renderEnd) + ". Are you sure?"
    prompt_start = cmds.confirmDialog( title='Confirm Render', message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    
    # ====================================== Make sure render settings are correct. ======================================
    toggle_render_settings()
    
    # ====================================== Actual Batch Render ======================================
    if prompt_start != "No":
        # Get list of render layers.
        render_layers = {cmds.getAttr( i + ".displayOrder") : i for i in cmds.ls(type='renderLayer')}
        render_layers.pop(0)  # Gets rid of "defaultRenderLayer"

        # Set only layer to default current layer.
        if useDefaultRenderLayer: render_layers = {0: "defaultRenderLayer"}

        # Batch Render.
        for index in render_layers:
            layer = render_layers[index]
            print("[ZOETROPE] Batch Render - Current Render Layer: " + str(layer))
            for frame in range(renderStart, renderEnd + 1):
                cmds.currentTime(frame)
                render_frame(width, height, frame, target_format, layer)

        # Exit message.
        cmds.confirmDialog(title='Animkit Zoetrope: Task Finished.', 
        message='Task finished. Successfully rendered all requested layers into target directory.', 
        button=['I got it!'], defaultButton='I got it!', dismissString='I got it!')


# =================================================== Zoetrope Formatter ===================================================
# Purpose: Use padding_format() to generate maya-like padding strings.
def get_numList(num):
    '''
    HELPER for padding_format().

    Returns a broken down list of numbers with appropriate "-"
    Example: get_numList(-24) -> ["-", "2", "4"] (Note the negative sign is its own char.)
    Example: get_numList(0) -> ["0"]
    Example: get_numList(24) -> ["2", "4"]
    '''
    # res function only accepts non-negative inputs.
    isNeg = False
    if (num < 0):
        num = num * -1
        isNeg = True
        
    # Create a list of individual number strings from a given number.
    res = list(map(str, [int(x) for x in str(num)]))

    # Add a negative sign string to the front of the list if the input number is negative.
    if(isNeg):
        res.insert(0, "-")
        
    return(res)

def make_num_list (listStart, listEnd):
    """
    HELPER for padding_format().

    Returns a list of numbers containing the last digit.
    Example: make_num_list(-24, 24) -> [-24, -23, ..., 0, 1, ..., 23, 24]
    """
    return [item for item in range(listStart, listEnd + 1)] 

def padding_format(number, padding):
    """
    Returns the correct padding of a number.
    Example: padding_format(-24, 4) -> "0-24"
    """
    if number >= 0:
        return ("%0" + str(padding) + "d") % number  # Positive + Zero Case
    else:
        number_list = get_numList(number)
        if len(number_list) > padding:
            # Should never occur but just in case.
            raise Exception("[ZOETROPE] ERROR: padding_format() - number_list is larger than padding!!!")
        elif len(number_list) < padding:
            need_zeroes = padding - len(number_list)
            for x in range(0, need_zeroes):
                number_list.insert(0, "0")
        
        return "".join(number_list)
    

# =================================================== Zoetrope Video Encoder ===================================================
def take_off_zero(input_str):
    """
    Takes off zero from the start of a string.
    Example: "0-10" -> "-10"
    """

    temp_str = input_str
    while temp_str[0] == "0":
        temp_str = temp_str[1:]
        if temp_str == "": return "0"  # Handle case when padding is 0000.

    return temp_str

def is_image(image_ext):
    if image_ext in ["jpg", "jpeg", "png", "tiff", "tif", "exr"]:
        return True
    else:
        return False

def get_start_end_frames(file_path, padding):
    """
    A function that takes in a folder and padding, figures out the start frame and end frame.
    """

    file_name_with_ext = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    padding_list = []

    for file_name_ext in file_name_with_ext:
        # Get file name.
        (file_name, ext) = os.path.splitext(file_name_ext)
        
        # Only include image files.
        if is_image(ext.replace('.', '') ):
            # Get last padding amount of character from the back of the file name.
            padding_str = file_name[-padding:]  

            # Convert padding to int, add it to the padding list
            padding_list.append(int(take_off_zero(padding_str)))
    
    return [min(padding_list), max(padding_list)]


def video_encoder(seq_folder, renders_prefix, image_format, target_format, frame_rate = get_frame_rate(), frame_padding = get_padding()):
    '''
    Encodes image sequence into respective file format.
    '''

    # Define constants
    frameStart = get_start_end_frames(seq_folder, frame_padding)[0]
    frameEnd = get_start_end_frames(seq_folder, frame_padding)[1]

    # Create temp folder
    temp_folder = seq_folder + "temp\\"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)
    print("[Zoetrope] Video Encoder - Successfully copied and renamed all images into a temporary folder at " + temp_folder + " .")

    # Make sequence list
    sequence_list = make_num_list(frameStart, frameEnd)
    for index, value in enumerate(sequence_list):
        sequence_list[index] = renders_prefix + "_" + padding_format(value, frame_padding) + "." + image_format
        
    # Copying everything into a new temp folder
    counter = 0
    for index, value in enumerate(sequence_list):
        source = seq_folder + value
        destination = temp_folder + padding_format(counter, frame_padding) + "." + image_format
        shutil.copyfile(source, destination) 
        # print("Processing the " + str(counter) + " image.") # Just to see progress
        counter += 1

    image_sequence_path = temp_folder + "%0"+ str (frame_padding) + "d." + image_format
    video_path = os.path.dirname(os.path.dirname(temp_folder)) + "\\" + renders_prefix + "." + target_format  # Go up one directory, need to test this code

    print("[Zoetrope] Video Encoder - Image sequence path: " + image_sequence_path)
    print("[Zoetrope] Video Encoder - Video target path: " + video_path)

    if os.path.exists(video_path): 
        os.remove(video_path)
        if not os.path.exists(video_path):
            print("[Zoetrope] Video Encoder - Video exists at: " + video_path + " and got deleted successfully.")
    
    subprocess.call(["ffmpeg", "-framerate", "24",  "-i", image_sequence_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", video_path], shell=True) 
    
    print("[Zoetrope] Video Encoder - Successfully encoded the image sequence to video of " + target_format + " format.")

    shutil.rmtree(temp_folder)
    print("[Zoetrope] Video Encoder - Successfully deleted the temporary folder at " + temp_folder + " .")


def assemble_sequence_folder(seq_folder, rendersPrefix = os.path.basename(sceneName().split('.')[0]), targetFormat = "mp4"):
    print("[Zoetrope] Sequence Folder Assembler - Current: " + seq_folder) 

    # Checking if the list is empty or not 
    if len(os.listdir(seq_folder)) == 0: 
        print("[Zoetrope] Video Converter - Empty directory at: " + seq_folder) 
    else: 
        # Sample a file and get extension of the files in the render folder
        isPicture = False
        ext = ""

        while(not isPicture):
            file_list = [f for f in os.listdir(seq_folder) if os.path.isfile(os.path.join(seq_folder, f))]
            for counter in range(len(file_list)):
                ext = os.path.splitext(file_list[counter])[1].replace('.', '') 
                if is_image(ext): isPicture = True

        if(isPicture):
            video_encoder(seq_folder = seq_folder, renders_prefix = rendersPrefix, image_format = ext, target_format = targetFormat)
        else:
            print("[Zoetrope] Video Converter - No image found at: " + seq_folder)

def video_converter(targetFormat):
    '''
    Calls video_encoder and convert all render layers into respective file format. 
    '''
    scene_path = cmds.file(location=True, query=True) 
    current_dir = sceneName().parent
    
    list_render_subfolders_with_paths = [x for x in os.listdir(current_dir + "/renders/") if os.path.isdir(current_dir + "/renders/" + x)]
    print("[Zoetrope] Video Converter - All avaliable render layers: " + str(list_render_subfolders_with_paths))

    for render_layer_folder in list_render_subfolders_with_paths:
        print("[Zoetrope] Video Converter - Current compositing render layer: " + render_layer_folder)
        current_layer_dir = os.path.dirname(scene_path)
        seq_folder = current_layer_dir + "/renders/" + render_layer_folder + "/"
        print("[Zoetrope] Video Converter - Current Sequence Folder: " + seq_folder)
        assemble_sequence_folder(seq_folder = seq_folder, targetFormat = targetFormat)


# =================================================== Zoetrope API ===================================================

def render_w_padding(self):
    TIMELINE = TimelineProperties()
    batch_render(renderStart = int(TIMELINE.START), renderEnd = int(TIMELINE.END))

def render_nopadding(self):
    TIMELINE = TimelineProperties()
    batch_render(renderStart = int(TIMELINE.INNER_START), renderEnd = int(TIMELINE.INNER_END))

def render_default_w_padding(self):
    TIMELINE = TimelineProperties()
    batch_render(renderStart = int(TIMELINE.START), renderEnd = int(TIMELINE.END), useDefaultRenderLayer = True)

def render_default_nopadding(self):
    TIMELINE = TimelineProperties()
    batch_render(renderStart = int(TIMELINE.INNER_START), renderEnd = int(TIMELINE.INNER_END), useDefaultRenderLayer = True)

def render_one_frame_png(self):
    toggle_render_settings()
    render_frame(width = get_resolution_settings("width"), height = get_resolution_settings("height"), frame=cmds.currentTime(query=True), file_format="png")

def render_one_frame_tif(self):
    toggle_render_settings()
    render_frame(width = get_resolution_settings("width"), height = get_resolution_settings("height"), frame=cmds.currentTime(query=True), file_format="tif")

def smart_convert_all_renders_compressed(self):
    video_converter(targetFormat = "mp4")

def smart_convert_all_renders_lossless(self):
    video_converter(targetFormat = "avi")


    