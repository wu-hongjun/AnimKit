from pymel.core import *
import maya.mel as mel
import maya.cmds as mc
import random as r
import shutil, subprocess, sys, getpass, time, os, platform

##############################################################################################

def run_mel(script_name):
        '''Runs a given MEL file'''
        print("Running MEL file: " + script_name)
        mel.eval("source " + script_name + ";")

##############################################################################################

# praise Cody
def praise_cody():
    mc.confirmDialog(title='AnimKit Loaded Successfully', 
    message='Praise the Savor of lights, Mighty king of squirrels, Finders of all Paths, and the creator of all clowns, Cody!', 
    button=['Anim!'], defaultButton='Anim!', dismissString='Anim!')

# Load AnimSchool Picker
def load_animschool_picker():
    mel.eval("loadPlugin AnimSchoolPicker.mll;")
    mel.eval("AnimSchoolPicker();")

# Load reParent
def load_reParent():
    run_mel('reparent_pro_v158.mel')

