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
class Mesh_Check(qg.QDialog):
    widgets = {};
    def __init__(self,parent = get_main_window()):
        super(Mesh_Check,self).__init__(parent)

        ##Checks if PySide window Exists##
        if window('Mesh_Check',ex=True) == True:
            deleteUI('Mesh_Check',wnd=True)

        #Window Setup
        self.setObjectName('Mesh_Check')
        self.setWindowTitle('Mesh Check')
        self.setWindowFlags(qc.Qt.Tool)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.setLayout(qg.QVBoxLayout())
        self.setMinimumWidth(475)
        self.setFixedHeight(150)
        
        #Check Topology
        i = 0
        self.widgets['topology_grid'] = qg.QFrame()
        self.widgets['topology_grid'].setLayout(qg.QGridLayout())
        for all in ['check_for_tris','check_for_n-gons','history','freeze_transforms']:
            self.widgets[all] = qg.QCheckBox(all.replace('_',' ').title())
            self.widgets[all].setChecked(True)
            self.widgets['topology_grid'].layout().addWidget(self.widgets[all],0,i)
            i += 1
        self.widgets['check_for_tris'].setFixedWidth(90)
        self.widgets['check_for_n-gons'].setFixedWidth(120)
        self.widgets['history'].setFixedWidth(60)
        self.widgets['freeze_transforms'].setFixedWidth(120)
        
        #Freeze and Delete History
        self.widgets['finalize_meshes'] = qg.QPushButton('Finalize Selected Meshes')
        self.widgets['finalize_meshes'].setMinimumHeight(75)
        
        #Layout
        self.layout().addWidget(self.widgets['topology_grid'])
        self.layout().addWidget(self.widgets['finalize_meshes'])
        
        #Functions
        self.widgets['finalize_meshes'].clicked.connect(self.finalize_mesh)
        
        self.show()

    def check_topology(self,obj,tris,ngons):
        faces = []
        if tris == True:
            select(obj + '.f[:]')
            polySelectConstraint(m = 3, t = 8, sz = 1)
            faces += ls(sl = True,fl = True)
            polySelectConstraint(sz = 0)
        
        if ngons == True:
            select(obj + '.f[:]')
            polySelectConstraint(m = 3, t = 8, sz = 3)
            faces += ls(sl = True,fl = True)
            polySelectConstraint(sz = 0)
        select(cl = True)    
        return faces
    
    def finalize_mesh(self):
        tris = self.widgets['check_for_tris'].isChecked()
        ngons = self.widgets['check_for_n-gons'].isChecked()
        history = self.widgets['history'].isChecked()
        freeze = self.widgets['freeze_transforms'].isChecked()
        bad_topology = []
        objs = ls(sl = True)
        for obj in objs: bad_topology += self.check_topology(obj,tris = tris, ngons = ngons)
        if bad_topology:
            select(bad_topology)
            refresh()
            confirmDialog(title = 'Bad Topology Detected!', message = 'Your selected meshes contain bad topology.', b = ['OK'], cb = 'OK')
        else: select(cl = True)
        for obj in objs:
            stops = []
            obj_history = listHistory(obj)
            children = obj.getChildren(s = True)
            for all in children: obj_history.remove(all)
            for all in obj_history:
                if all.nodeType() in ['blendShape','skinCluster']:
                    stops.append(all)
            if stops: confirmDialog(title = 'Important History Detected', message = 'Your selected meshes contain history that may be important.', b = ['OK'], cb = 'OK')
            else:
                if freeze == True: makeIdentity(obj,a=True,t=True,r=True,s=True)
                if history == True: delete(obj,ch = True)

#Mesh_Check() 