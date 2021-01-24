#Import api modules
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
from pymel.core import *
import time
import os
import shutil
import animkit_playblast_plus_vp2
import maya.cmds as cmds
import maya.mel as mel
import functools
import random
import subprocess  
import sys
import time 
from PySide2 import QtCore


def showErrorWindow(errorMessage):
        errW = window(t="!!!", w=150, h=100, sizeable=False)
        columnLayout( adjustableColumn=True, cal="center" )
        text( label=errorMessage, align="center")
        okayButton = button( label='Okay', command=Callback(errW.delete) )
        showWindow(errW)
        setFocus(okayButton)

def check_scene():
    sn = sceneName()
    if sn == '':
        showErrorWindow("ERROR!\nThis scene is not saved yet.")
        return None

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
    print("[Timelapse Creator] Capturing image number: " + str(nextImage))
    return nextImage
    
def get_next_image_dir():
    sn = sceneName()
    dir = sn.parent
    
    name = os.path.basename(sn).split('.')[0]
    timeLapseDir = os.path.join(dir, name+'_timelapse')
    print("[Timelapse Creator] Current Timelapse Directory: " + str(timeLapseDir))
    
    if not os.path.exists(timeLapseDir): os.makedirs(timeLapseDir)

    nextImageNum = getNextImageNumber(timeLapseDir)
    nextImageNumStr = "%(ver)08d" % {"ver":nextImageNum}
    
    nextImageFile = os.path.join(timeLapseDir,nextImageNumStr + ".png")

    return nextImageFile

def save_current_viewport_image_free_scale(img_location):
    # Deprecated, this will alow for flexible image size generation based on the window which isn't the best idea
    # Credit: https://stackoverflow.com/questions/44953145/capture-image-in-maya-2017-viewport2-0-in-python
    # Grab the last active 3d viewport
    view = apiUI.M3dView.active3dView()
    print("[Timelapse Creator] Viewport Width: " + str(view.portWidth()))
    print("[Timelapse Creator] Viewport Height: " + str(view.portHeight()))

    #read the color buffer from the view, and save the MImage to disk
    image = api.MImage()
    if view.getRendererName() == view.kViewport2Renderer:
        image.create(view.portWidth(), view.portHeight(), 4, api.MImage.kFloat)
        view.readColorBuffer(image)
        image.convertPixelFormat(api.MImage.kByte)
        # image.resize(1920, 1080, True)
        print("[Timelapse Creator] User using Viewport 2.0!")
    else:
        view.readColorBuffer(image)
        print("[Timelapse Creator] WARNING: User using other kind viewport!")
    image.writeToFile(img_location, 'png')

def save_image_from_current_cam(img_location, captureFrame=1, padding = 4):
    folder_location = "\\".join(img_location.split('\\')[:-1])

    try: res = PyNode("defaultResolution")
    except: res = None

    # Set playblast width
    if (res != None):     pbWidth = int(res.width.get())
    else:                   pbWidth = 1280  # Fallsafe
            
    # Set playblast height
    if (res != None):     pbHeight = int(res.height.get())
    else:                   pbHeight = 720  # Fallsafe

    output_file = cmds.playblast(startTime = captureFrame, 
                        endTime = captureFrame, 
                        forceOverwrite = True,
                        width = pbWidth, 
                        height = pbHeight,
                        fmt = "image", 
                        filename = folder_location + "temp", 
                        viewer = False, 
                        clearCache = True, 
                        showOrnaments = False, 
                        offScreen = True, 
                        percent = 100, 
                        compression = "png", 
                        quality = 100, fp = padding)
                        
    padding_format = "{:0>" + str(padding) + "d}"
    replace_padding_number = padding_format.format(captureFrame)
    output_temp_location = output_file.replace("####", replace_padding_number)
    os.rename(output_temp_location, img_location)

    print("[Timelapse Creator] Successfully created a snapshot at: " + img_location)









class BackgroundProcess(QtCore.QObject):
    """Monitor a process running in the background."""

    Finished = QtCore.Signal()
    Timeout = QtCore.Signal()

    def __init__(self, cmd, timeout=10.0):
        super(BackgroundProcess, self).__init__()

        self.cmd = cmd 
        self.timeout = timeout

        self.start_time = 0.0

    def run(self):
        process = subprocess.Popen(self.cmd, shell=True)
        print("[{}] {}".format(process.pid, self.cmd))

        self.start_time = time.time()

        while True:
            elapsed_time = time.time() - self.start_time

            if elapsed_time > self.timeout:
                self.Timeout.emit()
                break

            if process.poll() is not None:
                self.Finished.emit()
                break


class BackStageTracker(QtCore.QObject):
    """Test program to demonstrate running a process on a background thread."""

    def __init__(self):
        super(BackStageTracker, self).__init__()

        self.run_timer = QtCore.QTimer()
        self.run_timer.timeout.connect(functools.partial(self.tick))
        
        delay = random.randint(2, 5)
        cmd = 'ping -n {} 127.0.0.1 > nul'.format(delay)

        self.start_time = time.time()
        
        self.background_thread = QtCore.QThread()

        self.background_process = BackgroundProcess(cmd, timeout=5.0)
        self.background_process.moveToThread(self.background_thread)

        self.background_process.Finished.connect(self.background_thread.quit)
        self.background_process.Timeout.connect(self.background_thread.quit)
        self.background_process.Finished.connect(self.on_work_finished)
        self.background_process.Timeout.connect(self.on_work_timeout)

        self.background_thread.finished.connect(self.background_thread.deleteLater)
        self.background_thread.started.connect(self.background_process.run)

        self.background_thread.start() 
        self.run_timer.start(100)

    def tick(self):                   
        elapsed_time = time.time() - self.start_time
        print("Elapsed time: {:.1f} seconds.".format(round(elapsed_time, 2)))

    def on_work_finished(self):
        print("Work complete")
        self.exit()

    def on_work_timeout(self):
        print("Timeout error")
        self.exit()

    def exit(self):   
        self.run_timer.stop()

        # Wait for the thread to fully stop
        self.background_thread.wait()

        QtCore.QCoreApplication.instance().exit(0)           


def trigger_background_process():
    app = QtCore.QCoreApplication(sys.argv)
    prog = BackStageTracker()  
    sys.exit(app.exec_())

def create_timelapse_from_viewport():
    check_scene()
    save_image_from_current_cam(get_next_image_dir())

def create_timelapse_from_tlcam(tlcam = "tlcam"):
    check_scene()

    # setCameraCmd = "lookThroughModelPanel " + str(tlcam) + " modelPanel1;"
    # setCameraCmd = "lookThroughModelPanel tlcam modelPanel1;"
    # mel.eval("lookThroughModelPanel tlcam modelPanel1;")
    
    save_image_from_current_cam(get_next_image_dir())