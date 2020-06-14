from pymel.all import *
import maya.cmds as mc
from functools import partial
import maya.OpenMayaUI as mui

try:
    import shiboken2 as shiboken
    from PySide2 import QtCore as qc
    from PySide2 import QtWidgets as qg
except:
    import shiboken
    from PySide import QtCore as qc
    from PySide import QtGui as qg
#===============================================================#
def get_main_window():
    pointer = mui.MQtUtil.mainWindow();
    return shiboken.wrapInstance(long(pointer), qg.QWidget)
#===============================================================#
class AlignerUI(qg.QDialog):
    widgets = {}
    def __init__(self,parent = get_main_window()):
        super(AlignerUI, self).__init__(parent);
        ##Checks if PySide window Exists##
        if window('AlignUI',ex=True) == True:
            deleteUI('AlignUI',wnd=True)

        #Window Setup
        self.setLayout(qg.QVBoxLayout())
        self.setObjectName('AlignUI')
        self.setWindowTitle('Align Objects')
        self.setWindowFlags(qc.Qt.Tool)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.setMinimumSize(200,200)

        for type in ['translation','rotation']:
            label = qg.QLabel(type.title())
            label.setAlignment(qc.Qt.AlignCenter)
            self.layout().addWidget(label)
            self.widgets[type + '_grid'] = qg.QFrame()
            self.widgets[type + '_grid'].setLayout(qg.QGridLayout())
            self.layout().addWidget(self.widgets[type + '_grid'])
            i = 0
            for axis in ['x','y','z']:
                self.widgets[type + '_' + axis] = qg.QCheckBox(axis.title())
                self.widgets[type + '_' + axis].setChecked(True)
                self.widgets[type + '_grid'].layout().addWidget(self.widgets[type + '_' + axis],0,i)
                i += 1
        
        self.widgets['align_button'] = qg.QPushButton('Align Objects')
        self.widgets['align_button'].setMinimumHeight(100)
        self.layout().addWidget(self.widgets['align_button'])
        
        self.widgets['align_button'].clicked.connect(self.align_objects)
        self.show()


    def align_objects(self):
        if len(ls(sl = True)) > 1:
            pos_x = self.widgets['translation_x'].isChecked()
            pos_y = self.widgets['translation_y'].isChecked()
            pos_z = self.widgets['translation_z'].isChecked()
            rot_x = self.widgets['rotation_x'].isChecked()
            rot_y = self.widgets['rotation_y'].isChecked()
            rot_z = self.widgets['rotation_z'].isChecked()
            
            objs = ls(sl = True)[:-1]
            target = ls(sl = True)[-1]
            px,py,pz = xform(target, q= True, ws=True, rp=True)
            rx,ry,rz = xform(target, q=True, ws = True, ro = True)
            
            for obj in objs:
                opx,opy,opz = xform(obj, q= True, ws=True, rp=True)
                orx,ory,orz = xform(obj, q=True, ws = True, ro = True)
                
                if pos_x == False: px = opx
                if pos_y == False: py = opy
                if pos_z == False: pz = opz
                if rot_x == False: rx = orx
                if rot_y == False: ry = ory
                if rot_z == False: rz = orz
                
                move(px,py,pz, obj, rpr = True)
                xform(obj, ws=True,ro=(rx,ry,rz))
            #select(cl = True)