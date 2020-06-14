from PySide2 import QtCore as qc;
from PySide2 import QtWidgets as qg;
from pymel.all import *
import maya.cmds as mc
from functools import partial;
import shiboken2;
import maya
import maya.OpenMayaUI as mui;
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin;
import os;
#=======================================================================================================================================================#
def getMainWindow():
    pointer = mui.MQtUtil.mainWindow();
    return shiboken2.wrapInstance(long(pointer), qg.QWidget);
#=======================================================================================================================================================#
class CB_Button(qg.QPushButton):
    def __init__(self, title, width, height, parent = None):
        super(CB_Button,self).__init__(parent);
        style = (   'QPushButton {background:rgb(0,0,0);' + 
                    'font-style: italic;' + 
                    'font-family: lucida sans unicode;' + 
                    'color:rgb(0,255,40);' + 
                    'border-radius: ' + str(height/2) + 'px;}' +  
                    'QPushButton:hover {border-style: solid;' + 
                    'border-width:2px;' + 
                    'border-color: rgb(0,255,50)}' + 
                    'QPushButton:pressed {border-width: 4px;' + 
                    'font-weight: normal;}');
        if title:
            self.setText(title);
        if width:
            self.setMinimumWidth(width);
        if height:
            self.setMinimumHeight(height);
        
        self.setStyleSheet(style)
#=======================================================================================================================================================#
class Clipboard(MayaQWidgetDockableMixin,qg.QDialog):
    widgets = {};
    def __init__(self,parent = getMainWindow()):
        super(Clipboard,self).__init__(parent)

        ##Checks if PySide window Exists##
        #self.deleteInstances();
        if window('Clipboard',ex =True) == True:
            deleteUI('Clipboard',wnd=True)


        #Window Setup
        self.setObjectName('Clipboard');
        self.setWindowTitle('Clipboard');
        self.setWindowFlags(qc.Qt.Tool);
        self.setAttribute(qc.Qt.WA_DeleteOnClose);
        self.setLayout(qg.QVBoxLayout());
        self.setMinimumWidth(400);
        self.setMinimumHeight(500);
        self.resize(400, 500);
        
        #Layout
        self.widgets['script'] = qg.QTextEdit()
        self.buttons = qg.QFrame()
        self.buttons.setLayout(qg.QVBoxLayout())
        self.buttons.setFixedHeight(150)
        
        self.layout().addWidget(self.widgets['script'])
        self.layout().addWidget(self.buttons)
        
        #Buttons
        btns = ['load_autoRig_script','save_autoRig_script','run_script','clear']
        for btn in btns:
            self.widgets[btn] = CB_Button((btn.replace('_',' ').title()),None,30)
            self.buttons.layout().addWidget(self.widgets[btn])
        
        self.widgets['load_autoRig_script'].clicked.connect(self.load_script)
        self.widgets['save_autoRig_script'].clicked.connect(self.save_script)
        self.widgets['run_script'].clicked.connect(self.run_script)
        self.widgets['clear'].clicked.connect(self.clear)
        
        #Show
        self.show();
        
    def deleteInstances(self):
        mayaMainWindowPtr = mui.MQtUtil.mainWindow() 
        mayaMainWindow = shiboken2.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow);
        # Go through main window's children to find any previous instances
        for obj in mayaMainWindow.children():
            if type( obj ) == maya.app.general.mayaMixin.MayaQDockWidget:
                if obj.widget().objectName() == 'Clipboard':
                    # If they share the same name then remove it
                    mayaMainWindow.removeDockWidget(obj)
                    # Delete it for good
                    obj.setParent(None)
                    obj.deleteLater()
                    
    def load_script(self):
        try:
            thisDir = os.path.dirname(mc.file(q=1, loc=1))
            items = os.listdir(thisDir)
            scripts = None
            for item in items:
                if item.endswith('.py') == True:
                    if 'autoRig' in item:
                        script = thisDir + '/' + item
            if script:
                string = open(script,'r')
                self.widgets['script'].setText(string.read())
                string.close()
                
        except:
            message = ('There are a few things that may have gone wrong:\n' + 
                      '1.) No autoRig script exists in this directory.\n' + 
                      '2.) The autoRig script is not saved as a .py file.\n')
            problem = confirmDialog(t = 'ERROR',m = message,b = ['OK'],cb = 'OK')
    
    def save_script(self):
        try:
            thisDir = os.path.dirname(mc.file(q=1, loc=1))
            items = os.listdir(thisDir)
            string = self.widgets['script'].toPlainText()
            script = None
            for item in items:
                if item.endswith('.py') == True:
                    if 'autoRig' in item:
                        script = thisDir + '/' + item
            if script:
                message = 'Are you sure you want to overwrite ' + script.replace(thisDir + '/','') + '?'
                overwrite = confirmDialog(t = 'File Already Exists!',m = message,b = ['Yes','No'],cb = 'No')
                if overwrite == 'Yes':
                    doc = open(script,'w').write(string)
            else:
                doc = open(thisDir + '/autoRig_script.py','w').write(string)
                message = 'An autoRig_script python file has been created.'
                directory = confirmDialog(t = 'SUCCESS',m = message,b = ['OK'],cb = 'OK')
                
        except:
            message = 'This file is not saved in a specific location.'
            directory = confirmDialog(t = 'ERROR: File Location',m = message,b = ['OK'],cb = 'OK')
        
    def run_script(self):
        code = {}
        string = compile(self.widgets['script'].toPlainText(),'<string>','exec')
        exec string in code

    def clear(self):
        message = 'Are you sure you want to clear the script?'
        clear = confirmDialog(t = 'Clear Script:',m = message,b = ['Yes','No'],cb = 'No')
        if clear == 'Yes':
            self.widgets['script'].setText('')
