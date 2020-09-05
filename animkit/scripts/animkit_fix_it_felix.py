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

# =================================================== FixNURBS ===================================================
def rebuild_surface_cmd(surface, caching = "1", 
                        replaceOriginal = "1", 
                        endKnots = "1", 
                        keepRange = "0", 
                        keepControlPoints = "0", 
                        keepCorners = "0"):
    
    general_cmds = " -ch " + caching + " -rpo " + replaceOriginal + " -end " + endKnots
    keep_cmds = " -kr " + keepRange + " -kcp " + keepControlPoints + " -kc " + keepCorners
    surface_cmd = " \"" + surface + "\""
    
    cmd = "rebuildSurface" + general_cmds + keep_cmds + surface_cmd
    return cmd


def fix_broken_NURBS(self):
    surface_list = cmds.ls(type='nurbsSurface')
    for surface in surface_list:
        command = rebuild_surface_cmd(surface)
        # print("Evaluating the following script: " + command)
        try:
            mel.eval(command) 
            # mel.eval("catchQuiet (" + command + ");")   # This does not work :(
        except RuntimeError:
            print("[Fix-it-Felix] Failed to rebuild the following surface: " + surface)
        except:
            print("[Fix-it-Felix] Unknown error occured while trying to execute the following command: " + command)
    print("[Fix-it-Felix] Fix Broken NURBS - Successfully rebuilt all NURBS Surfaces.")

# =================================================== FixArnold ===================================================
def fix_defaultArnoldDriver_pre(self):
    '''
    Sets the defaultArnoldDriver.pre to its original state of "".
    '''
    cmds.setAttr("defaultArnoldDriver.pre", "", type="string")
    print("[Fix-it-Felix] Fix Arnold Global - Successfully fixed defaultArnoldDriver.pre settings to original.")