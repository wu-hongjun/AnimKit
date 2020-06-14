from PySide2 import QtCore as qc;
from PySide2 import QtWidgets as qg;
from pymel.all import *
import maya.cmds as mc
import os
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt
from functools import partial;
import shiboken2;
import maya.OpenMayaUI as mui;

#=======================================================================================================================================================#
def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow();
    return shiboken2.wrapInstance(long(pointer), qg.QMainWindow);
#=======================================================================================================================================================#
class ShapeShifter(qg.QDialog):
    widgets = {};
    def __init__(self,parent = getMayaWindow()):
        super(ShapeShifter,self).__init__(parent);
        if window('ShapeShifter',ex=True) == True:
                deleteUI('ShapeShifter',wnd=True)
        
        self.setObjectName('ShapeShifter');
        self.setWindowTitle('Shape Shifter');
        self.setWindowFlags(qc.Qt.Tool);
        self.setAttribute(qc.Qt.WA_DeleteOnClose);
        self.setLayout(qg.QGridLayout());
        self.setMinimumWidth(450);
        self.setMinimumHeight(300);
        i=0;
        
        self.widgets['start_buttons'] = qg.QGridLayout()
        start_btns = ['save_shape_factory','create_working_anims','export_anim_shapes']
        for all in start_btns:
            self.widgets[all] = qg.QPushButton(all.replace('_',' ').title())
            self.widgets[all].clicked.connect(partial(self.startFunctions,all))
            self.widgets[all].setMinimumHeight(30)
            self.widgets['start_buttons'].layout().addWidget(self.widgets[all],0,i)
            i=i+1;
        
        fileN = mc.file(q=True, sn=True, shn=True)
        if fileN != 'animShapes_factory.ma':
            self.widgets['create_working_anims'].setEnabled(False)
            self.widgets['export_anim_shapes'].setEnabled(False)
        
        if objExists('working_anims')==True:
            self.widgets['create_working_anims'].setEnabled(False)
            self.widgets['export_anim_shapes'].setEnabled(True)
        
        self.widgets['add_shapes'] = qg.QPushButton('Add Shapes')
        self.widgets['replace_shapes'] = qg.QPushButton('Replace Shapes')
        self.widgets['mirror_shapes'] = qg.QPushButton('Mirror Shapes')
        self.widgets['add_shapes'].clicked.connect(partial(self.transfer_shapes,type='add'))
        self.widgets['replace_shapes'].clicked.connect(self.transfer_shapes)
        self.widgets['mirror_shapes'].clicked.connect(self.mirrorShapes)
        self.widgets['add_shapes'].setMinimumHeight(50)
        self.widgets['replace_shapes'].setMinimumHeight(50)
        self.widgets['mirror_shapes'].setMinimumHeight(50)
        
        self.layout().addLayout(self.widgets['start_buttons'],0,0)
        self.layout().addWidget(self.widgets['add_shapes'],1,0)
        self.layout().addWidget(self.widgets['replace_shapes'],2,0)
        self.layout().addWidget(self.widgets['mirror_shapes'],3,0)
        
        self.show()
    
    def startFunctions(self,function,*arg):
        if function == 'save_shape_factory':
            self.create_anim_shapes_factory();
            self.widgets['create_working_anims'].setEnabled(True)
            if objExists('working_anims')==True:
                self.widgets['create_working_anims'].setEnabled(False)
            self.widgets['export_anim_shapes'].setEnabled(True)
            
        elif function == 'create_working_anims':
            self.create_working_anims();
            self.widgets['create_working_anims'].setEnabled(False)
        else:
            self.export_anim_shapes();
            
    def create_anim_shapes_factory(self,*arg):
        fileN = mc.file(q=True, sn=True, shn=True)
        thisDir = os.path.dirname(cmds.file(q=1, loc=1))
        saveAs((thisDir+"\\animShapes_factory.ma"),f=True,typ='mayaAscii')
        if fileN != 'animShapes_factory.ma':
            openFile((thisDir+"\\animShapes_factory.ma"),f=True)
        
    def create_working_anims(self,*arg):
        anims = ls("*.animNode", o=1, r=1)+ls("*_switch", r=1)
    
        if (objExists("working_anims")):
            extractedAnimsGrp = PyNode("working_anims")
        else:
            extractedAnimsGrp = group(em=1, n="working_anims")
        
        oldNames = map(lambda n: n.nodeName(), extractedAnimsGrp.getChildren())
        
        for a in anims:
            if a.nodeName() in oldNames: continue
            if not isinstance(a, nt.Transform):
                "NOT A TRANSFORM: "+a.nodeName()
                continue
                
            animGhost = group(em=1)
            delete(parentConstraint(a, animGhost, mo=0))
            delete(scaleConstraint(a, animGhost, mo=0))
            parent(animGhost, extractedAnimsGrp)
            animGhost.rename(a.nodeName())
            
            animShapes = a.getChildren(s=1)
            for ash in animShapes:
                parent(ash, animGhost, s=1, add=1, r=1)
                
            print "ADDED: "+a.nodeName()
            
        for all in listRelatives('working_anims'):
            rename(all,all.replace('_anim','_working_anim'))
            
        select('*component_grp')
        for all in ls(sl=True):
            PyNode(all).visibility.set(0)
        select(cl=True)
    
    def export_anim_shapes(self,*arg):
        for all in listRelatives('working_anims'):
            rename(all,all.replace('_working_anim','_anim'))
        
        animsGrp = PyNode('working_anims')
        animsFileName = os.path.join(sceneName().dirname(), 'animShapes.ma')
        
        dupGrp = duplicate(animsGrp)
        dupGrp[0].rename('anims')
        select(dupGrp)
        exportSelected(animsFileName, type="mayaAscii", constructionHistory=0, expressions=0, shader=0, constraints=0, channels=0, preserveReferences=0, f=1)
        select(cl=1)
        delete(dupGrp)
        for all in listRelatives('working_anims'):
            rename(all,all.replace('_anim','_working_anim'))
        
    def alignPR(self,obj,target):
        alPos = xform(target, q= True, ws=True, rp=True);
        alRot = xform(target, q=True, ws = True, ro = True);
        move(alPos[0],alPos[1],alPos[2], obj, rpr = True);
        xform(obj, ws=True,ro=(alRot[0],alRot[1],alRot[2]))

    def alignPiv(self,obj,target,*arg):
        alPos = xform(target, q= True, ws=True, rp=True);
        move(alPos[0],alPos[1],alPos[2], obj+'.rotatePivot', obj+'.scalePivot', rpr = True);

    def transfer_shapes(self,type = 'replace',*arg):
        if len(ls(sl=True)) > 1:
            objs = ls(sl=True)[:-1]
            target = ls(sl=True)[-1]
    
            if type == 'replace':
                try:
                    tgtShapes = target.getChildren(s=True)
                    delete(tgtShapes)
                except:
                    tgtShapes = PyNode(target).getChildren(s=True)
                    delete(tgtShapes)
            
            for obj in objs:
                parent(obj,target)
                self.alignPiv(obj,target)
                makeIdentity(obj,a=True,t=True,r=True,s=True)
                delete(obj,ch=True)
                refresh()
                objShapes = obj.getChildren(s=True)
                parent(objShapes, target, r=True,s=True)
                delete(obj)
                delete(target,ch=True)
            select(cl=True)
            
    def transfer_shapesB(self,objs,target,type = 'replace',*arg):
        if type == 'replace':
            try:
                tgtShapes = target.getChildren(s=True)
                delete(tgtShapes)
            except:
                tgtShapes = PyNode(target).getChildren(s=True)
                delete(tgtShapes)
        
        for obj in objs:
            parent(obj,target)
            self.alignPiv(obj,target)
            makeIdentity(obj,a=True,t=True,r=True,s=True)
            delete(obj,ch=True)
            refresh()
            objShapes = obj.getChildren(s=True)
            parent(objShapes, target, r=True,s=True)
            delete(obj)
            delete(target,ch=True)
        select(cl=True)
            
    def mirrorShapes(self,*arg):
        objs = ls(sl=True)
        select(cl=True)
        for obj in objs:
            if obj.endswith('anim') == True or obj.endswith('switch') == True:
                if objExists('world_grp*')==True:
                    delete('world_grp*')
                world = group(n=('world_grp'),em=True)
                new_obj = group(n=('new_grp'),em=True,p=world)
                self.alignPR(new_obj,obj)
                
                dup = duplicate(obj)[0]
                dup.translateX.unlock()
                dup.translateY.unlock()
                dup.translateZ.unlock()
                dup.rotateX.unlock()
                dup.rotateY.unlock()
                dup.rotateZ.unlock()
                dup.scaleX.unlock()
                dup.scaleY.unlock()
                dup.scaleZ.unlock()
                
                self.transfer_shapesB([dup],new_obj)
                world.scaleX.set(-1)
                makeIdentity(world,a=True,t=True,r=True,s=True)
                
                if 'left' in str(obj):
                    obj = obj.replace('left','right')
                    self.transfer_shapesB([new_obj],obj)
                elif 'right' in str(obj):
                    obj = obj.replace('right','left')
                    self.transfer_shapesB([new_obj],obj)
                else:
                    confirmDialog(title='ERROR', message = 'Selected anim does not have a left or right side.',b = ['OK']);
                delete(world)
                for shape in PyNode(obj).getChildren(s=True):
                    try:
                        reverseSurface(shape,d=0,ch=False,rpo=1)
                    except:
                        try:
                            polyNormal(shape, nm = 4,unm = 1, ch=False)
                        except:
                            pass
                select(cl=True)

ShapeShifter()