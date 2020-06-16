from pymel.core import *
import maya.mel as mel
import maya.cmds as cmds
import random as r
import shutil, subprocess, sys, getpass, time, os, platform

##############################################################################################

def create_render_cam_from_view():
    cameraTransform = cmds.modelEditor(cmds.getPanel(withLabel = 'Persp View'), query = True, camera = True)
    cameraShape = cmds.listRelatives(cameraTransform, type = 'camera')[0]
    newCameraName = "render_cam"
    # newCameraName = '%s_NEW' % cameraTransform

    cmds.duplicate(cameraShape, name = newCameraName)
    cmds.showHidden(newCameraName)
    cmds.select(newCameraName, replace = True)

