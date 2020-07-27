from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import shutil, subprocess, sys, getpass, time, os, platform
from mtoa.cmds.arnoldRender import arnoldRender

# Version Info
version = "2.0.0"
update = "July 18, 2020"
new = "Zoetrope 2.0 brings bug fixes as well as new features like automatic padding detection, frame range prompt, etc."

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

def get_resolution_settings(attr):
    return cmds.getAttr("%s.%s"%("defaultResolution", attr))
    
def render_frame(width, height, frame, file_format="tif", render_layer = "defaultRenderLayer"):
    file_dir = (sceneName().parent + "\\renders\\" + render_layer).replace('\\', '/')
    prepend = os.path.basename(sceneName()).split('.')[0]
    cmds.setAttr("defaultArnoldDriver.ai_translator", file_format, type="string")
    cmds.setAttr("defaultArnoldDriver.pre", file_dir + "\\" + prepend, type="string")
    cmds.setAttr("render_camShape.mask", 1)
    arnoldRender(width, height, True, True,'render_cam', ' -layer ' + render_layer)

def batch_render(renderStart, renderEnd, width = get_resolution_settings("width"), height = get_resolution_settings("height"), target_format = "tif", useDefaultRenderLayer = False):
    # Prompt user to check render range.
    msg = "Will render from frame " + str(renderStart) + " to frame " + str(renderEnd) + ". Are you sure?"
    prompt_start = cmds.confirmDialog( title='Confirm Render', message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

    if prompt_start != "No":
        # Get list of render layers.
        render_layers = {cmds.getAttr( i + ".displayOrder") : i for i in cmds.ls(type='renderLayer')}
        render_layers.pop(0)  # Gets rid of "defaultRenderLayer"

        # Set only layer to default current layer.
        if useDefaultRenderLayer: render_layers = {0: "defaultRenderLayer"}

        # Batch Render.
        for index in render_layers:
            layer = render_layers[index]
            print("[ZOETROPE]: Current Render Layer: ", layer)
            for frame in range(renderStart, renderEnd + 1):
                cmds.currentTime(frame)
                render_frame(width, height, frame, target_format, layer)

        # Exit message.
        cmds.confirmDialog(title='Animkit Zoetrope: Task Finished.', 
        message='Task finished. Successfully batch rendered all requested layers into target directory.', 
        button=['I got it!'], defaultButton='I got it!', dismissString='I got it!')

def mp4_encoder(renders_dir, renders_prefix, frame_rate = 24 , frame_padding = 4, 
                  image_format = "tif", target_format = "mp4"):
    
    image_sequence_path = renders_dir + renders_prefix + "%0" + str(frame_padding) + "d." + image_format
    video_path = renders_dir + renders_prefix + "." + target_format
    
    print("[Zoetrope] Image sequence path: " + image_sequence_path)
    print("[Zoetrope] Video target path: " + video_path)
    
    subprocess.call(["ffmpeg", "-framerate", str(frame_rate), "-i", 
                     image_sequence_path, video_path])
    
    print("[Zoetrope] Successfully encoded the image sequence to video of " + target_format + "format.")

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

def render_one_frame(self):
    TIMELINE = TimelineProperties()
    render_frame(width = get_resolution_settings("width"), height = get_resolution_settings("height"), frame=TIMELINE.INNER_START)

def smart_convert_all_renders(self):
    scene_path = cmds.file(location=True, query=True) 
    current_dir = os.path.dirname(scene_path)
    list_render_subfolders_with_paths = [f.name for f in os.scandir(current_dir) if f.is_dir()]
    for render_layer_folder in list_render_subfolders_with_paths:
        # The weird _1_ is a way to get rid of a bug lol
        mp4_encoder(renders_dir = current_dir, renders_prefix = os.path.basename(sceneName()).split('.')[0] + "_1_")
