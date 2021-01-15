#Import api modules
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
from pymel.core import *
import time
import os
import shutil
import animkit_playblast_plus_vp2

#Grab the last active 3d viewport
view = apiUI.M3dView.active3dView()

def getNextImageNumber(imageDir):
    imageFiles = []
    items = os.listdir(imageDir)
    for item in items:
        if item.endswith('.png') == True:
            imageFiles.append(item)
    nextImage = -1
    for f in imageFiles:
        name = os.path.basename(f).split('.')[0]
        itrImageStr = name.split(".")[0]
        try:
            itrImage = int(itrImageStr)
            if itrImage > nextImage:
                nextImage = itrImage
        except ValueError:
            continue
    nextImage += 1
    return nextImage
    
def get_next_image_dir():
    sn = sceneName()
    dir = sn.parent
    
    name = os.path.basename(sn).split('.')[0]
    timeLapseDir = os.path.join(dir, name+'_timelapse')
    print("[Timelapse Creator] Current Timelapse Directory: " + str(timeLapseDir))
    
    if not os.path.exists(timeLapseDir): os.makedirs(timeLapseDir)

    nextImageNum = getNextImageNumber(timeLapseDir)
    nextImageNumStr = "%(ver)03d" % {"ver":nextImageNum}
    
    nextImageFile = os.path.join(timeLapseDir,nextImageNumStr + ".png")

    return nextImageFile

def save_one_image(img_location):
    # Credit: https://stackoverflow.com/questions/44953145/capture-image-in-maya-2017-viewport2-0-in-python
    #read the color buffer from the view, and save the MImage to disk
    image = api.MImage()
    if view.getRendererName() == view.kViewport2Renderer:      
        image.create(view.portWidth(), view.portHeight(), 4, api.MImage.kFloat)
        view.readColorBuffer(image)
        image.convertPixelFormat(api.MImage.kByte)
        print("WARNING: User using other kind viewport !")
    else:
        view.readColorBuffer(image)
        print("WARNING: User using other kind viewport !")
    image.writeToFile(img_location, 'png')
    
def create_timelapse(self):
    save_one_image(get_next_image_dir())
