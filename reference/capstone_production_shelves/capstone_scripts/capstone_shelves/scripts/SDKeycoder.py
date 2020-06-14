from PySide2 import QtCore as qc;
from PySide2 import QtWidgets as qg;
from pymel.all import *
import maya.cmds as mc
import os
from functools import partial;
import shiboken2;
import maya
import maya.OpenMayaUI as mui;
import clipboardUI as cb
reload(cb)
#=======================================================================================================================================================#
def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow();
    return shiboken2.wrapInstance(long(pointer), qg.QMainWindow);
#=======================================================================================================================================================#
class SDK_Button(qg.QPushButton):
    def __init__(self, title, width, height, parent = None):
        super(SDK_Button,self).__init__(parent);
        style = (   'QPushButton {background:rgb(0,0,0);' + 
                    'font-style: italic;' + 
                    'font-family: lucida sans unicode;' + 
                    'color:rgb(0,255,40);' + 
                    'border-radius: ' + str(height/3) + 'px;}' +  
                    'QPushButton:hover {border-style: solid;' + 
                    'border-width:2px;' + 
                    'border-color: rgb(0,255,50)}' + 
                    'QPushButton:pressed {border-width: 4px;' + 
                    'font-weight: normal;}');
        self.txt = None;
        if title:
            self.setText(title);
        if width:
            self.setMinimumWidth(width);
        if height:
            self.setMinimumHeight(height);
        
        self.setStyleSheet(style)

class SDK_Frame(qg.QFrame):
    def __init__(self,name,width,height,parent = None):
        super(SDK_Frame,self).__init__(parent)
        if width:
            self.setMinimumWidth(width);
        if height:
            self.setFixedHeight(height);

        self.setFrameStyle(qg.QFrame.Panel | qg.QFrame.Raised);
        self.setLineWidth(2);
#=======================================================================================================================================================#
class SDK_Coder(qg.QDialog):
    widgets = {};
    def __init__(self,parent = getMayaWindow()):
        super(SDK_Coder,self).__init__(parent);
        if window('SDK_Coder',ex=True) == True:
            deleteUI('SDK_Coder',wnd=True)
        
        self.setObjectName('SDK_Coder');
        self.setWindowTitle('Set Driven Keycoder');
        self.setWindowFlags(qc.Qt.Tool);
        self.setAttribute(qc.Qt.WA_DeleteOnClose);
        self.setLayout(qg.QVBoxLayout());
        self.setMinimumWidth(400);
        self.setMinimumHeight(500);
        self.resize(400, 500);
        
        self.widgets['columns'] = qg.QHBoxLayout()
        self.widgets['script'] = qg.QTextEdit()
        self.widgets['create_script_button'] = SDK_Button('Key / Create Script',None,30)
        self.widgets['copy_to_clipboard'] = SDK_Button('Open / Copy To Clipboard',None,30)
        
        self.layout().addLayout(self.widgets['columns'])
        self.layout().addWidget(self.widgets['script'])
        self.layout().addWidget(self.widgets['create_script_button'])
        self.layout().addWidget(self.widgets['copy_to_clipboard'])
        
        for all in ['driver','driven']:
            #Column
            self.widgets[all + '_column'] = SDK_Frame((all + '_layout'),None,250)
            self.widgets[all + '_layout'] = qg.QFormLayout()
            self.widgets[all + '_column'].setLayout(self.widgets[all + '_layout'])
            self.widgets['columns'].addWidget(self.widgets[all + '_column'])
            
            #Title
            title = '-   ' + (''.join([(x + '  ') for x in all.title()])) + '   -'
            self.widgets[all + '_title'] = qg.QLabel(title)
            self.widgets[all + '_title'].setAlignment(qc.Qt.AlignCenter)
            self.widgets[all + '_layout'].layout().addRow(self.widgets[all + '_title'])
            style = 'QLabel {font-weight: bold; font-family; lucida sans unicode; font-size: 12px;}'
            self.widgets[all + '_title'].setStyleSheet(style)
            
            #Info Button Setup
            self.widgets[all] = qg.QLineEdit()
            self.widgets[all + '_get'] = SDK_Button('>>',30,20,None)
            self.widgets[all + '_lay'] = qg.QHBoxLayout()
            
            self.widgets[all + '_lay'].layout().addWidget( self.widgets[all])
            self.widgets[all + '_lay'].layout().addWidget( self.widgets[all + '_get'])
            self.widgets[all + '_layout'].addRow(self.widgets[all + '_lay'])
            
            #Attribute List
            self.widgets[all + '_list'] = qg.QListWidget()
            self.widgets[all + '_list'].setFixedHeight(175)
            self.widgets[all + '_layout'].addRow(self.widgets[all + '_list'])
        
        self.widgets['driver_get'].clicked.connect(self.get_driver)
        self.widgets['driven_get'].clicked.connect(self.get_driven)
        self.widgets['create_script_button'].clicked.connect(self.create_script)
        self.widgets['copy_to_clipboard'].clicked.connect(self.copy_to_clipboard)
        self.widgets['driven_list'].setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
        
        self.show()
        
    def get_driver(self):
        if len(ls(sl=True)) > 0:
            obj = ls(sl=True)[0]
        else:
            obj_text = self.widgets['driver'].text()
            if obj_text:
                obj = PyNode(obj_text)
        try:
            self.widgets['driver'].setText(obj.name())
            attrs = listAttr(obj,w=True,u=True,v=True,k=True)
                
            self.widgets['driver_list'].clear();
            self.widgets['driver_list'].addItems(attrs);
        except:
            print 'ERROR: Something is wrong!'
            
    def get_driven(self):
        if len(ls(sl=True)) > 0:
            objs = ls(sl=True)
        else:
            obj_text = self.widgets['driven'].text()
            if obj_text:
                objs = [PyNode(x) for x in list(obj_text.split(','))]
        try:        
            names = []
            all_attrs = []
            for obj in objs:
                names += obj.name() + ','
                all_attrs += listAttr(obj,w=True,u=True,v=True,k=True)
            self.widgets['driven'].setText((''.join(names))[:-1])
            
            attrs = list(set([x for x in all_attrs if all_attrs.count(x) > (len(objs)-1)]))
                
            self.widgets['driven_list'].clear();
            self.widgets['driven_list'].addItems(attrs);
        except:
            print 'ERROR: Something is wrong!'   
        
    def create_script(self):
        try:
            driver = self.widgets['driver'].text()
            driven = list(self.widgets['driven'].text().split(','))
            
            driver_attr = self.widgets['driver_list'].selectedItems()[0]
            driven_attrs = self.widgets['driven_list'].selectedItems();
            
            cd = driver + '.' + driver_attr.text()
            dv = Attribute(cd).get()
            
            string = self.widgets['script'].toPlainText()
            
            for obj in driven:
                for attr in driven_attrs:
                    dn = obj + '.' + attr.text()
                    v = Attribute(dn).get()
                    
                    string = string + "setDrivenKeyframe( '" + dn + "', cd = '" + cd +"', dv = " + str(dv) + ", v= " + str(v) + ")\n"
                    
                    setDrivenKeyframe(dn ,cd = cd,dv = dv, v= v)
    
            self.widgets['script'].setText(string)
        except:
            print 'ERROR: Something is wrong!'
    
    
    def copy_to_clipboard(self):
        clipboard_on = False
        mayaMainWindowPtr = mui.MQtUtil.mainWindow() 
        mayaMainWindow = shiboken2.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow);
        
        for obj in mayaMainWindow.children():
            if type( obj ) == maya.app.general.mayaMixin.MayaQDockWidget:
                if obj.widget().objectName() == 'Clipboard':
                    if obj.widget().isVisible() == False:
                        mayaMainWindow.removeDockWidget(obj)
                        obj.setParent(None)
                        obj.deleteLater()
                        clipboard_on = False
                    else:
                        clipboard_on = True
                        clipboard = obj.widget()
        
        if clipboard_on == False:
            clipboard = cb.Clipboard()
        else:
            string = self.widgets['script'].toPlainText()
            clip_text = clipboard.widgets['script'].toPlainText()
            if clip_text:
                clipboard.widgets['script'].setText(clip_text  + '\n' + string)
            else:
                clipboard.widgets['script'].setText(clip_text + string)
#=======================================================================================================================================================#
#SDK_Coder()