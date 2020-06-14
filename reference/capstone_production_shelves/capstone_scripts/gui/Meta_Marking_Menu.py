import pymel.all as pm
import metaCore2 as meta
import maya.cmds as mc
import os
import gui.GuiUtilities as guts
import MARS as mars
import MARS.MarsUtilities as mu
from functools import partial
reload(mars)
reload(mu)
reload(meta)
import maya.OpenMayaUI as mui
import shiboken2 as shiboken
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg
#===============================================================#  
def rerun_component_by_node(node):
    type = node.network_type.get()
    if type == 'Character_Rig': return meta.Character_Rig('',pm.listConnections(node.root)[0])
    if type == 'COG_Chain': return meta.COG_Chain('','',pm.listConnections(node.start)[0],'')
    if type == 'FK_Chain': return meta.FK_Chain('','',pm.listConnections(node.start)[0],'')
    if type == 'RFK_Chain': return meta.RFK_Chain('','',pm.listConnections(node.start)[0],'')
    if type == 'FKIK_Arm': return meta.FKIK_Arm('','',pm.listConnections(node.start)[0],'')
    if type == 'FKIK_Biped_Leg': return meta.FKIK_Biped_Leg('','',pm.listConnections(node.start)[0],'','','','','')
    if type == 'Flexible_Mouth':
        corners = pm.listConnections(node.corner_lip_bones)
        return meta.Flexible_Mouth('','',['',''],['',''],corners[0],'','')
    if type == 'Flexible_Eyelid':
        corners = pm.listConnections(node.corner_lid_bones)
        return meta.Flexible_Eyelid('','',['',''],['',''],corners[0],'','')
    if type == 'Face_Component': return meta.Face_Component('','',pm.listConnections(node.bones))
    if type == 'Eye_Aim_Anims': return meta.Eye_Aim_Anims('','',pm.listConnections(node.eyes))

def mars_component_rerun(node):
    type = node.node_type.get()
    if type == 'CharacterRig': return mars.CharacterRig('','',node = node)
    if type == 'COGChain': return mars.COGChain('','','','',node = node)
    if type == 'FKChain': return mars.FKChain('','','','',node = node)
    if type == 'RFKChain': return mars.RFKChain('','','','',node = node)
    if type == 'EyeAimComponent': return mars.EyeAimComponent('','','','',node = node)
    if type == 'FaceComponent': return mars.FaceComponent('','','',node = node)
    if type == 'MultiConstraint': return mars.MultiConstraint('','',node = node)
    if type == 'DeformerStack': return mars.DeformerStack('','','','','',node = node)
    if type == 'FKIKSplineChain': return mars.FKIKSplineChain('','','','',node = node)
    if type == 'FKIKRibbonChain': return mars.FKIKRibbonChain('','','','',node = node)
    if type == 'FKIKArm': return mars.FKIKArm('','','','',node = node)
    if type == 'FKIKBipedLeg': return mars.FKIKBipedLeg('','','','','','','','',node = node)
    if type == 'FKIKBendyArm': return mars.FKIKArm('','','','',[],[],node = node)
    if type == 'FKIKBendyBipedLeg': return mars.FKIKBendyBipedLeg('','','','','','','','',[],[],node = node)

def quick_align():
    selection = pm.ls(sl = True)
    for i, obj in enumerate(selection):
        try:
            node = guts.acquire_nodes(selection[i])[0]
            component = mars_component_rerun(node)
            switch = pm.PyNode(component.get_switch())
            if switch.FKIK_switch.get() == 0: component.FK_to_IK_switch()
            else: component.IK_to_FK_switch()
        except: pass
    pm.select(cl = True)
    
class MultiConUI(qw.QDialog):
    widgets = {};
    def __init__(self,parent = guts.get_main_window()):
        super(MultiConUI,self).__init__(parent)
        
        ##Checks if PySide window Exists##
        if pm.window('Multi_Constraints',ex=True) == True: pm.deleteUI('Multi_Constraints',wnd=True)
                
        #Window Setup
        self.setObjectName('Multi_Constraints')
        self.setWindowTitle('Multi Constraints')
        self.setWindowFlags(qc.Qt.Tool)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        guts.widget_setup(self,qw.QVBoxLayout(),spacing = None, cm = (0,0,0,0))
        self.setFixedSize(500,300)
        
        #Scroll
        self.tab_layout = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 0, cm = (0,0,0,0))
        self.tabs = qw.QScrollArea()
        self.tabs.setWidgetResizable(True);
        self.tabs.setWidget(self.tab_layout)
        
        #Layout
        self.layout().addWidget(self.tabs)

        self.resize(300,300);
        self.add_tabs()
        self.widgets['script_job'] = pm.scriptJob( e= ["SelectionChanged",self.add_tabs])
        self.show()
        
    def get_multi_constraint(self,anim):
        if anim.hasAttr('connected_to'):
            nodes = pm.listConnections(anim.connected_to)
            for node in nodes:
                if node.hasAttr('version'):
                    if node.node_type.get() == 'MultiConstraint':
                        if pm.listConnections(node.constraint_anim)[0] == anim: return node
                else:
                    if node.network_type.get() == 'Multi_Constraint':
                        if pm.listConnections(node.anim)[0] == anim: return node
    
    def add_tabs(self):
        tabs = self.tab_layout.children()[1:]
        for tab in tabs: tab.deleteLater()
        if len(pm.ls(sl = True)) > 0:
            for anim in pm.ls(sl = True):
                if anim.hasAttr('parent_to'):
                    #Tab
                    self.widgets[anim + '_tab'] = guts.widget_setup(qw.QFrame(),qw.QFormLayout(),cm = None, spacing = None)
                    self.widgets[anim + '_tab'].setFrameStyle(qw.QFrame.Box | qw.QFrame.Plain)
                    self.widgets[anim + '_tab'].setFixedHeight(110)
                    
                    #Combo Box
                    self.widgets[anim + '_cons'] = qw.QComboBox()
                    node = self.get_multi_constraint(anim)
                    
                    if node.hasAttr('influences'): influences = pm.listConnections(node.influences)
                    else: influences = pm.listConnections(node.influence_nulls)
                    
                    for influence in influences: self.widgets[anim + '_cons'].addItem(influence.name())
                    self.widgets[anim + '_cons'].setCurrentIndex(anim.parent_to.get())

                    #Align
                    self.widgets[anim + '_align_check'] = qw.QCheckBox()
                    self.widgets[anim + '_align_check'].setChecked(True)

                    #Button
                    self.widgets[anim + '_apply'] = qw.QPushButton('Apply')

                    #Tab Layout
                    self.widgets[anim + '_tab'].layout().addRow(qw.QLabel(anim.name()))
                    self.widgets[anim + '_tab'].layout().addRow('Parent To: ',self.widgets[anim + '_cons'])
                    self.widgets[anim + '_tab'].layout().addRow('Align: ',self.widgets[anim + '_align_check'])
                    self.widgets[anim + '_tab'].layout().addRow(self.widgets[anim + '_apply'])
                    self.tab_layout.layout().addWidget(self.widgets[anim + '_tab'])
                    
                    #Functions
                    self.widgets[anim + '_apply'].clicked.connect(partial(self.multi_constraint_switch,anim))

    def multi_constraint_switch(self,anim,*arg):
        align = False
        index = self.widgets[anim + '_cons'].currentIndex()
        if self.widgets[anim + '_align_check'].isChecked(): align = True
        mu.constraint_switch(anim,index,align = align)
        
    def closeEvent(self, event):
        pm.scriptJob(kill = self.widgets['script_job'])
        
#===============================================================#  
def delete_metacore_marking_menu():
    if pm.popupMenu("metacore_marking_menu", exists=1) == True: pm.deleteUI("metacore_marking_menu")

class MetaMarkingMenu():
    def __init__(self, parent = "viewPanes"):
        if (pm.popupMenu("metacore_marking_menu", exists=1)): pm.deleteUI("metacore_marking_menu")
        if parent == 'viewPanes': main = pm.popupMenu("metacore_marking_menu",button = 1, ctl = 1, alt =0, sh = 1, allowOptionBoxes =1, parent = 'viewPanes', mm=1)
        else: main = pm.popupMenu('metacore_marking_menu',allowOptionBoxes =1, parent = parent,mm = 1)
        
        tool_menu = pm.menuItem(p = main, sm = True, label = "Tool Orientation", rp="SW")
        pm.menuItem(p = tool_menu, label = 'Move: World', rp = 'NW', en = True, c = "maya.cmds.manipMoveContext('Move', e = True, mode = 2)")
        pm.menuItem(p = tool_menu, label = 'Move: Object', rp = 'W', en = True, c = "maya.cmds.manipMoveContext('Move', e = True, mode = 0)")
        pm.menuItem(p = tool_menu, label = 'Move: Parent', rp = 'SW', en = True, c = "maya.cmds.manipMoveContext('Move', e = True, mode = 1)")    
        pm.menuItem(p = tool_menu, label = 'Rotate: World', rp = 'S', en = True, c = "maya.cmds.manipRotateContext('Rotate', e = True, mode = 1)")
        pm.menuItem(p = tool_menu, label = 'Rotate: Object', rp = 'SE', en = True, c = "maya.cmds.manipRotateContext('Rotate', e = True, mode = 0)")
        
        pose_menu = pm.menuItem(p = main, sm = True, label = "Animation Tools", rp="N")
        pm.menuItem(p = pose_menu, label = "Open Puppet Master", rp="N",c = partial(self.puppet_master_win))
        pm.menuItem(p = pose_menu, label = "Open Graph Editor", rp="NW",c = partial(self.graph_editor))
        pm.menuItem(p = pose_menu, label = "Show Motion Trail", rp="NE", c = partial(self.add_motion_trail))
        pm.menuItem(p = pose_menu, label = "Open Meta Character Picker", rp="E", c = partial(self.character_picker_win))
        
        sel = pm.ls(sl = True)
        if sel:
            try: node = guts.acquire_nodes(sel[0])[0]
            except: node = None
            if node != None:
                rigs = guts.rig_check()
                
                select_menu = pm.menuItem(p = main, sm = True, label = "Select Anims", rp="NE", c = partial(self.select_anims,'complete_rig'))
                pm.menuItem(p = select_menu, label = 'Component', rp = 'N', en = True, c = partial(self.select_anims,'component'))
                pm.menuItem(p = select_menu, label = 'Hierarchy', rp = 'NE', en = True, c = partial(self.select_anims,'hierarchy'))
                if rigs:
                    pm.menuItem(p = select_menu, label = 'Rig', rp = 'E', en = True, c = partial(self.select_anims,'rig'))
                    pm.menuItem(p = select_menu, label = 'Entire Character', rp = 'SE', en = True, c = partial(self.select_anims,'complete_rig'))
    
                key_menu = pm.menuItem(p = main, sm = True, label = "Key Anims", rp = "E", c = partial(self.key_anims,'complete_rig'))
                pm.menuItem(p = key_menu, label = 'Key Selected', rp = 'N', en = True, c = partial(self.key_anims,'anim'))
                pm.menuItem(p = key_menu, label = 'Key Component', rp = 'NE', en = True, c = partial(self.key_anims,'component'))
                pm.menuItem(p = key_menu, label = 'Key Hierarchy', rp = 'E', en = True, c = partial(self.key_anims,'hierarchy'))
                if rigs:
                    pm.menuItem(p = key_menu, label = 'Key Rig', rp = 'SE', en = True, c = partial(self.key_anims,'rig'))
                    pm.menuItem(p = key_menu, label = 'Key Entire Character', rp = 'S', en = True, c = partial(self.key_anims,'complete_rig'))
                
                default_menu = pm.menuItem(p = main, sm = True, label = "Default Pose", rp = "S", c = partial(self.set_default_pose,'complete_rig'))
                pm.menuItem(p = default_menu, label = 'Selected', rp = 'S', en = True, c = partial(self.set_default_pose,'anim'))
                pm.menuItem(p = default_menu, label = 'Component', rp = 'SE', en = True, c = partial(self.set_default_pose,'component'))
                pm.menuItem(p = default_menu, label = 'Hierarchy', rp = 'E', en = True, c = partial(self.set_default_pose,'hierarchy'))
                if rigs:
                    pm.menuItem(p = default_menu, label = 'Rig', rp = 'SW', en = True, c = partial(self.set_default_pose,'rig'))
                    pm.menuItem(p = default_menu, label = 'Entire Character', rp = 'W', en = True, c = partial(self.set_default_pose,'complete_rig'))
                
                if node.hasAttr('switch'):
                    switch_menu = pm.menuItem(p = main, sm = True, label = "Switch", rp = "SE", c = partial(self.switch_FKIK,'align_switch'))
                    pm.menuItem(p = switch_menu, label = 'Switch Only', rp = 'S', en = True, c = partial(self.switch_FKIK,'switch'))
                    pm.menuItem(p = switch_menu, label = 'Align Switch', rp = 'SE',en = True, c = partial(self.switch_FKIK,'align_switch'))
                    pm.menuItem(p = switch_menu, label = 'Key Align Switch', rp = 'E',en = True, c = partial(self.switch_FKIK,'key_switch'))

                if sel[0].hasAttr('parent_to'):
                    constraint_menu = pm.menuItem(p = main, sm = False, label = "Multi Constraint", rp = "W", c = self.multi_con_win)
                
                mirror_menu = pm.menuItem(p = main, sm = True, label = "Mirror", rp = "NW", en = True, c = partial(self.mirror_pose,'anim'))
                pm.menuItem(p = mirror_menu, label = 'Mirror Selected', rp = 'NE', en = True,c = partial(self.mirror_pose,'anim'))
                pm.menuItem(p = mirror_menu, label = 'Mirror Component', rp = 'N', en = True,c = partial(self.mirror_pose,'component'))
                pm.menuItem(p = mirror_menu, label = 'Mirror Hierarchy', rp = 'NW', en = True,c = partial(self.mirror_pose,'hierarchy'))
                if rigs:
                    pm.menuItem(p = mirror_menu, label = 'Mirror Rig', rp = 'W', en = True, c = partial(self.mirror_pose,'rig'))
                    pm.menuItem(p = mirror_menu, label = 'Mirror Entire Character', rp = 'SW', en = True, c = partial(self.mirror_pose,'complete_rig'))
    
    def rig_info(self,node):
        rig, root = None, None
        if node.hasAttr('topCon'): rig = node
        elif node.hasAttr('rig'): rig = pm.listConnections(node.rig)[0]
        if rig != None: root = guts.get_root_rig(rig)
        return rig, root
    
    def character_picker_win(self,*args):
        from gui.Meta_Character_Picker import MetaCharacterPicker
        win = MetaCharacterPicker()
    
    def multi_con_win(self,*args):
        win = MultiConUI()
    
    def puppet_master_win(self,*args):
        from gui.Puppet_Master import PuppetMaster
        win = PuppetMaster()
         
    def graph_editor(self,*args):
        for graph in pm.getPanel(sty="graphEditor") or []: pm.scriptedPanel(graph, e=True, to=True)
    
    def add_motion_trail(self,*args):
        for all in pm.ls(sl=True):
            pm.snapshot(all, mt =  True, i = 1, st= pm.playbackOptions(q = True, min = True),et = pm.playbackOptions(q = True, max = True))
    
    def set_default_pose(self,type,*args):
        for obj in pm.ls(sl = True):
            node = guts.acquire_nodes(obj)[0]
            rig, root = self.rig_info(node)
            if type == 'anim': mu.set_to_default_pose(obj)
            elif type == 'component': self.reapply_class_functions(node).default_pose()
            elif type == 'hierarchy': self.reapply_class_functions(node).hierarchy_default_pose()
            elif type == 'rig': self.reapply_class_functions(rig).rig_default_pose()
            elif type == 'complete_rig': self.reapply_class_functions(rig).complete_rig_default_pose()
                
    def mirror_pose(self,type,*args):
        objs = pm.ls(sl = True)
        if type == 'anim': self.mirror_selection(objs)
        else:
            anims = []
            for obj in objs:
                node = guts.acquire_nodes(obj)[0]
                rig, root = self.rig_info(node)
                if type == 'component': anims += self.reapply_class_functions(node).get_all_anims()
                elif type == 'hierarchy': anims += self.reapply_class_functions(node).get_hierarchy_anims()
                elif type == 'rig': anims += self.reapply_class_functions(rig).get_rig_anims()
                elif type == 'complete_rig': anims += self.reapply_class_functions(rig).get_complete_rig_anims()
            self.mirror_selection(anims)
    
    def key_anims(self, type, *args):
        for obj in pm.ls(sl = True):
            node = guts.acquire_nodes(obj)[0]
            rig, root = self.rig_info(node)
            if type == 'anim':
                for attr in obj.listAttr(w=True,u=True,v=True,k=True):
                    attribute = attr.split('.')[-1]
                    pm.setKeyframe(obj,at = attribute)
            elif type == 'component': self.reapply_class_functions(node).key_all_anims()
            elif type == 'hierarchy': self.reapply_class_functions(node).key_hierarchy()
            elif type == 'rig': self.reapply_class_functions(rig).key_all_rig_anims()
            elif type == 'complete_rig': self.reapply_class_functions(rig).key_complete_rig_anims()
    
    def select_anims(self,type,*args):
        for obj in pm.ls(sl = True):
            node = guts.acquire_nodes(obj)[0]
            rig, root = self.rig_info(node)
            if type == 'component': self.reapply_class_functions(node).select_all_anims()
            elif type == 'hierarchy': self.reapply_class_functions(node).select_hierarchy_anims()
            elif type == 'rig' and rig != None: self.reapply_class_functions(rig).select_rig_anims()
            elif type == 'complete_rig': self.reapply_class_functions(rig).select_complete_rig_anims()

    def switch_FKIK(self,type,*args):
        for obj in pm.ls(sl = True):
            node = guts.acquire_nodes(obj)[0]
            if node.hasAttr('node_type'): component = mars_component_rerun(node)
            else: component = self.reapply_class_functions(node)
            switch = pm.PyNode(component.get_switch())
                
            if type == 'switch':
                if switch.FKIK_switch.get() == 0: switch.FKIK_switch.set(1)
                else: switch.FKIK_switch.set(0)
            elif type == 'align_switch':
                if switch.FKIK_switch.get() == 0: component.FK_to_IK_switch()
                else: component.IK_to_FK_switch()
            elif type == 'key_switch':
                current_frame = pm.currentTime(q = True)
                previous_frame = current_frame - 1.0
                pm.currentTime(previous_frame)
                component.key_all_anims()
                pm.currentTime(current_frame)
                if switch.FKIK_switch.get() == 0: component.FK_to_IK_switch()
                else: component.IK_to_FK_switch()
                component.key_all_anims()
                    
    def reapply_class_functions(self,node):
        if node.hasAttr('node_type'): return mars_component_rerun(node)
        else: return rerun_component_by_node(node)
        
    def mirror_selection(self,anims,*args):
        attrs = []
        values = []
        for anim in anims:
            if anim.hasAttr('animNode'):
                v = []
                components = list(set([str(x.node_type.get()) for x in pm.listConnections(anim.connected_to) if x.hasAttr('anims') and anim in pm.listConnections(x.anims)]))
                attrs.append(anim.listAttr(w=True,u=True,v=True,k=True))
                for attr in anim.listAttr(w=True,u=True,v=True,k=True):
                    if str(attr).startswith('center_'):
                        if '.rotate' in str(attr):
                            if 'COGChain' in components:
                                if str(attr).endswith('translateX') or str(attr).endswith('rotateY') or str(attr).endswith('rotateZ'): v.append(attr.get() * -1.00)
                                else: v.append(attr.get())
                            else:
                                if str(attr).endswith('Z'): v.append(attr.get()) 
                                else: v.append(attr.get() * -1.00)
                        else:
                            if str(attr).endswith('translateX'): v.append(attr.get() * -1.00)
                            else: v.append(attr.get())
                    else: v.append(attr.get())
                values.append(v)
        for i, att in enumerate(attrs):
            for k, a in enumerate(att):
                if 'left' in a.name(): rev_a = pm.Attribute(a.name().replace('left_','right_'))
                elif 'right' in a.name(): rev_a = pm.Attribute(a.name().replace('right_','left_'))
                else: rev_a = pm.Attribute(a.name())
                rev_a.set(values[i][k])