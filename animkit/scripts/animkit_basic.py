from pymel.core import *
import maya.mel as mel
import maya.cmds as mc
import random as r
import shutil, subprocess, sys, getpass, time, os

##############################################################################################

# Install required packages

# install: Install a package by calling sys and pip.
# Takes in a str package and calls "pip install package". 
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

##############################################################################################

# simple cube for testing
def createPolyCube(*args):
    mc.polyCube()

# Create a basic Yes/No dialog.
def confirm_box():
    mc.confirmDialog( title='Confirm', message='Are you sure?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

# lol
def praise_cody():
    mc.confirmDialog( title='Praise Cody', message='Praise the Savor of lights, Mighty king of squirrels, and the creator of all clowns, Cody!', button=['Anim!'], defaultButton='Anim!', dismissString='Anim!')
