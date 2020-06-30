from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import shutil, subprocess, sys, getpass, time, os, platform
from mtoa.cmds.arnoldRender import arnoldRender

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

def render_frame(width, height, frame, file_format="png", render_layer = "defaultRenderLayer"):
    file_dir = os.path.join(sceneName().parent, render_layer).replace('\\', '/')
    print("file_dir: ", file_dir)
    prepend = os.path.basename(sceneName()).split('.')[0] + "_" +str(frame)
    print("prepend: ", prepend)
    cmds.setAttr("defaultArnoldDriver.ai_translator", file_format, type="string")
    cmds.setAttr("defaultArnoldDriver.pre", file_dir + "\\" + prepend, type="string")
    arnoldRender(width, height, True, True,'render_cam', ' -layer ' + render_layer)

def prompt_exit():
    cmds.confirmDialog(title='Animkit Zoetrope: Task Finished.', 
        message='Task finished. Successfully batch rendered all requested layers into target directory.', 
        button=['I got it!'], defaultButton='I got it!', dismissString='I got it!')

def batch_render(start, end, width, height, target_format = "png", usePadding = False, useDefaultRenderLayer = False):
    if usePadding:
        renderStart = start - 25
        renderEnd = end + 24
    else:
        renderStart = start
        renderEnd = end

    render_layers = {cmds.getAttr( i + ".displayOrder") : i for i in cmds.ls(type='renderLayer')}

    if useDefaultRenderLayer: render_layers = {0: "defaultRenderLayer"}

    for index in render_layers:
        # Batch Render
        layer = render_layers[index]
        print("Current Layer: ", layer)
        frame_counter = 0  # Can't have png sequence with negative index.
        for frame in range(renderStart, renderEnd + 1):
            cmds.currentTime(frame)
            render_frame(width, height, frame_counter, target_format, layer)
            frame_counter += 1

        # Get rid of the weird _1 file name issue.
        file_dir = os.path.join(sceneName().parent, layer).replace('\\', '/')
        for render in os.listdir(file_dir):
            if render.endswith(".png"):
                os.rename(file_dir + "\\" + render, file_dir + "\\" + render.replace("_1.png", ".png"))

    prompt_exit()


def get_render_settings(attr):
    return cmds.getAttr("%s.%s"%("defaultRenderGlobals", attr))

def get_resolution_settings(attr):
    return cmds.getAttr("%s.%s"%("defaultResolution", attr))
    
def render_w_padding(self):
    TIMELINE = TimelineProperties()
    batch_render(start = int(TIMELINE.INNER_START), 
                    end = int(TIMELINE.INNER_END), 
                    width = get_resolution_settings("width"), 
                    height = get_resolution_settings("height"), 
                    target_format = "png", 
                    usePadding = True)

def render_nopadding(self):
    TIMELINE = TimelineProperties()
    batch_render(start = int(TIMELINE.INNER_START), 
                    end = int(TIMELINE.INNER_END), 
                    width = get_resolution_settings("width"), 
                    height = get_resolution_settings("height"), 
                    target_format = "png", 
                    usePadding = False)

def render_default_w_padding(self):
    TIMELINE = TimelineProperties()
    batch_render(start = int(TIMELINE.INNER_START), 
                    end = int(TIMELINE.INNER_END), 
                    width = get_resolution_settings("width"), 
                    height = get_resolution_settings("height"), 
                    target_format = "png", 
                    usePadding = True,
                    useDefaultRenderLayer = True)

def render_default_nopadding(self):
    TIMELINE = TimelineProperties()
    batch_render(start = int(TIMELINE.INNER_START), 
                    end = int(TIMELINE.INNER_END), 
                    width = get_resolution_settings("width"), 
                    height = get_resolution_settings("height"), 
                    target_format = "png", 
                    usePadding = False, 
                    useDefaultRenderLayer = True)
