import pymel.all as pm
import maya.cmds as mc
from functools import partial
import maya, os
import maya.mel as mel
import xml.etree.ElementTree as ET
import maya.OpenMaya as om
import maya.OpenMayaUI as mui
import gui.GuiUtilities as guts
import shiboken2 as shiboken
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg
reload(guts)
#=================================================================================================================#
def load_path_weights(path):
    selection = pm.ls(sl = True)
    if len(selection) > 0:
        items = os.listdir(path)
        for obj in selection:
            if obj.name() + '.xml' in items:
                doc = ET.parse(path + '/' + obj.name() + '.xml')
                root = doc.getroot()
                bones = doc.findall('bones')[0]
                joint_names = [str(x.get('id')) for x in bones.findall('joint')]
                joints = [pm.PyNode(x) for x in joint_names]
                max = 4
                    
                try: pm.delete(pm.listHistory(pm.ls(sl = True),type = 'skinCluster'))
                except: pass
                
                skin = obj.name() + '_skin'
                mesh = root.find('mesh')
                try: max = int(mesh.get('max_influences'))
                except: pass
                vertices = mesh.findall('vert')
                
                try:
                    pm.skinCluster(joints,obj,n = skin,tsb = True, mi = max, sm = 1, nw = 1)
                    pm.progressWindow(title='Loading...',pr=0, st= obj.replace('_',' ').title() + ': 0%', ii = False)
                    percent = 100.00/float(len(vertices))
                    pm.refresh()
                    
                    for k, vert in enumerate(vertices):
                        zeroes = []
                        zeroes += joint_names
                        progress = percent * (k + 1)
                        pm.progressWindow(e=1, pr=progress, st= obj.replace('_',' ').title() + ': %d%%' % progress)
                        vertex = str(vert.get('id'))
                        influences = []
                        for data in vert.findall('influence'):
                            influences.append((str(data.get('id')),float(data.get('value'))))
                            zeroes.remove(str(data.get('id')))
                        for zero in zeroes: influences.append((str(zero),0.0))
                        pm.skinPercent(skin,vertex,tv = influences)
                        pm.refresh()
                except: pass
                
                pm.progressWindow(endProgress=1)
                pm.refresh()
                pm.select(cl = True)
#====================================================================================================================#
class FunctionIcon(qw.QPushButton):
    def __init__(self,pic,parent = None):
        super(FunctionIcon,self).__init__(parent)
        self.pic = pic
        
    def paintEvent(self,event):
        self.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)  
        
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
        
        rect = qc.QRect(0,0,option.rect.width()-1,option.rect.height()-1)
        center = qc.QPoint((option.rect.width() * 0.5) - 10,(option.rect.height() * 0.5))
        
        pixmap = qg.QPixmap(self.pic)
        pixmap.scaled(10,10,qc.Qt.IgnoreAspectRatio, qc.Qt.SmoothTransformation)
        pix_rect = qc.QRect(0,0,option.rect.height(),option.rect.height())

        painter.drawPixmap(pix_rect,pixmap)
        self.setFixedWidth(option.rect.height())
#====================================================================================================================#
class WeightList(qw.QDialog):
    widgets = {}
    def __init__(self,parent = guts.get_main_window()):
        super(WeightList,self).__init__(parent)
        
        ##Checks if PySide window Exists##
        for win in ['Weight_List']:
            if pm.window(win,ex=True) == True: pm.deleteUI(win,wnd=True)
                
        #Window Setup
        self.setObjectName('Weight_List')
        self.setWindowTitle('Weight List')
        self.setWindowFlags(qc.Qt.Tool)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        guts.widget_setup(self,qw.QVBoxLayout(),cm = (5,5,5,5),spacing = 5)
        self.setMinimumWidth(300)
        self.setMinimumHeight(550)
        
        self.change_vertex = None
        self.previous_index = None
        
        #File Path
        self.path_frame = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 2, cm = (2,2,2,2),add_to = self)
        self.path_frame.setFrameStyle(qw.QFrame.StyledPanel)
        self.path_frame.setFixedHeight(35)
        
        self.path = self.get_path(open = True)
        self.path_label = guts.widget_setup(qw.QLabel(self.path),None,add_to = self.path_frame)
        self.find_path_btn = guts.widget_setup(qw.QPushButton('>>>'),None,add_to = self.path_frame)
        self.find_path_btn.setFixedSize(30,25)

        #Buttons
        self.save_load_frame = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 5,add_to = self)
        for x in ['save_weights','load_weights']:
            self.widgets[x + '_btn'] = guts.widget_setup(qw.QPushButton(x.replace('_',' ').title()),None,add_to = self.save_load_frame)
            self.widgets[x + '_btn'].setFixedHeight(35)
        self.save_preferences_btn = guts.widget_setup(qw.QPushButton('Save Preferences'),None,add_to = self)
        self.save_preferences_btn.setFixedHeight(25)
        
        #Fuction Stack
        self.function_stack = guts.widget_setup(qw.QStackedWidget(),None,add_to = self)
        self.starting_button_setup()
        
        #Functions
        self.widgets['save_weights_btn'].clicked.connect(self.save_weights)
        self.widgets['load_weights_btn'].clicked.connect(self.load_weights)
        self.save_preferences_btn.clicked.connect(self.save_preferences)
        self.find_path_btn.clicked.connect(self.get_path)
        self.edit_influences_setup()
        self.edit_vertex_skin_weights_setup()
        self.edit_averaged_vertex_skin_weights()
        self.soft_select_to_skin_weight_setup()
        self.add_influence_setup()
        self.widgets['selection_influences'] = pm.scriptJob( e= ["SelectionChanged",self.get_influences])
        self.refresh_timer()
        self.resize(425,325)
        self.show()
    
    #===============================================================================================================================#
    #Setups
    #===============================================================================================================================#          
    def starting_button_setup(self):
        self.start_frame = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),cm = (5,5,5,5),spacing = 5)
        self.start_frame.setFrameStyle(qw.QFrame.StyledPanel)
        self.function_stack.addWidget(self.start_frame)
        
        btns = ['copy_skin_weights','mirror_skin_weights','hammer_skin_weights','edit_influences',
                'edit_vertex_skin_weights','edit_averaged_vertex_weights','soft_select_to_skin_weight']
        for btn in btns:
            btn_grid = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),add_to = self.start_frame)
            
            label = btn.replace('_',' ').title()
            pic = '{0}icons/{1}.png'.format(pm.internalVar(upd = True),btn)
            icon = guts.widget_setup(FunctionIcon(pic),None,add_to = btn_grid)
            self.widgets['{0}_btn'.format(btn)] = guts.widget_setup(qw.QPushButton(label),None,add_to = btn_grid)
            self.widgets['{0}_btn'.format(btn)].setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)  
            
        self.widgets['copy_skin_weights_btn'].clicked.connect(self.copy_skin_weights)
        self.widgets['mirror_skin_weights_btn'].clicked.connect(self.mirror_skin_weights)
        self.widgets['hammer_skin_weights_btn'].clicked.connect(self.hammer_skin_weights)
        self.widgets['edit_influences_btn'].clicked.connect(partial(self.change_index,1))
        self.widgets['edit_vertex_skin_weights_btn'].clicked.connect(partial(self.change_index,2))
        self.widgets['edit_averaged_vertex_weights_btn'].clicked.connect(partial(self.change_index,3))
        self.widgets['soft_select_to_skin_weight_btn'].clicked.connect(partial(self.change_index,4))
    
    def edit_influences_setup(self):
        #Influence Section
        self.function_frame = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),cm = (5,5,5,5),spacing = 5)
        self.function_frame.setFrameStyle(qw.QFrame.StyledPanel)
        self.function_stack.addWidget(self.function_frame)
        
        #Edit Section
        edit_section = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = 5,add_to = self.function_frame)
        for i, x in enumerate(['current','non']):
            section = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),add_to = edit_section)
            label = guts.center_label(x.title() + ' Influences',widget = section)
            label.setStyleSheet('font-size: 10pt; font-weight: bold;')
            label.setFixedHeight(25)
            
            self.widgets[x + '_influences'] = guts.widget_setup(qw.QListWidget(),None,add_to = section)
            self.widgets[x + '_influences'].setSelectionMode(qw.QAbstractItemView.ExtendedSelection)
            
            filter_area = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),cm = (0,5,0,5),spacing =  5,add_to = section)
            filter_area.setFixedHeight(30)
            
            f_label = guts.widget_setup(qw.QLabel('Filter: '),None,add_to = filter_area)
            self.widgets[x + '_filter'] = guts.widget_setup(qw.QLineEdit(),None,add_to = filter_area)
            self.widgets[x + '_filter'].textChanged.connect(self.get_influences)
            
            if i == 0:
                edit_btns = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = edit_section)
                edit_btns.layout().setAlignment(qc.Qt.AlignTop)
                st_label = guts.center_label('',widget = edit_btns)
                edit_btns.setFixedWidth(30)
                st_label.setFixedHeight(20)
                
                self.add_influence_btn = guts.widget_setup(qw.QPushButton('<<'),None,add_to = edit_btns)
                self.remove_influence_btn = guts.widget_setup(qw.QPushButton('>>'),None,add_to = edit_btns)
                self.add_influence_btn.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
                self.remove_influence_btn.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
                
                e_label = guts.center_label('',widget = edit_btns)
                e_label.setFixedHeight(25)
        
        back_btn = self.back_button(widget = self.function_frame)
        
        #Functions
        self.add_influence_btn.clicked.connect(self.add_influences_to_skin)
        self.remove_influence_btn.clicked.connect(self.remove_influences_from_skin)
    
    def edit_vertex_skin_weights_setup(self):
        self.vert_frame = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.function_stack.addWidget(self.vert_frame)
        
        self.vert_layout = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (1,1,1,1))
        self.vert_layout.layout().setAlignment(qc.Qt.AlignTop)
        vert_scroll = guts.widget_setup(qw.QScrollArea(),None,add_to = self.vert_frame)
        vert_scroll.setWidgetResizable(True)
        vert_scroll.setWidget(self.vert_layout)
        
        back_btn = self.back_button(widget = self.vert_frame)
    
    def edit_averaged_vertex_skin_weights(self):
        self.average_frame = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.function_stack.addWidget(self.average_frame)
        
        self.average_layout = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (1,1,1,1))
        self.average_layout.layout().setAlignment(qc.Qt.AlignTop)
        average_scroll = guts.widget_setup(qw.QScrollArea(),None,add_to = self.average_frame)
        average_scroll.setWidgetResizable(True)
        average_scroll.setWidget(self.average_layout)
        
        back_btn = self.back_button(widget = self.average_frame)
        
    def soft_select_to_skin_weight_setup(self):
        falloff = pm.softSelect(q = True,ssd = True)
        
        convert_frame = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),spacing = 5,cm = (5,5,5,5))
        convert_frame.setFrameStyle(qw.QFrame.StyledPanel)
        self.function_stack.addWidget(convert_frame)
        
        menu_section = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = convert_frame)
        self.skin_influences = guts.widget_setup(qw.QListWidget(),None,add_to = menu_section)
        
        filter_area = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),cm = (0,5,0,5),spacing =  5,add_to = menu_section)
        filter_area.setFixedHeight(30)
        guts.widget_setup(qw.QLabel('Filter: '),None,add_to = filter_area)
        
        self.skinning_filter = guts.widget_setup(qw.QLineEdit(),None,add_to = filter_area)
        self.skinning_filter.textChanged.connect(self.get_influences)
        
        settings = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = menu_section)
        self.falloff_slider = guts.widget_setup(AttributeSlider('Falloff Radius',spin_max = 10,value = falloff),None,add_to = settings)
        self.falloff_slider.hidden_spin.valueChanged.connect(self.falloff_radius_changed)
        self.highest_weight = guts.widget_setup(AttributeSlider('Highest Weight',value = 1.00),None,add_to = settings)
        
        apply_button = guts.widget_setup(qw.QPushButton('Convert Soft Selection To Skin Weights'),None,add_to = menu_section)
        apply_button.setFixedHeight(75)
        apply_button.clicked.connect(self.convert_soft_selection_to_skinweights)
        
        back_btn = self.back_button(widget = convert_frame)
    
    def add_influence_setup(self):
        self.add_influence_frame = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.function_stack.addWidget(self.add_influence_frame)
        
        self.vtx_influences = guts.widget_setup(qw.QListWidget(),None,add_to = self.add_influence_frame)
        self.vtx_influences.setSelectionMode(qw.QAbstractItemView.ExtendedSelection)
            
        filter_area = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),cm = (0,5,0,5),spacing =  5,add_to = self.add_influence_frame)
        filter_area.setFixedHeight(30)
            
        f_label = guts.widget_setup(qw.QLabel('Filter: '),None,add_to = filter_area)
        self.vtx_filter = guts.widget_setup(qw.QLineEdit(),None,add_to = filter_area)
        self.vtx_filter.textChanged.connect(self.get_influences)
        
        self.apply_influence_btn = guts.widget_setup(qw.QPushButton('Apply Selected Influences'),None,add_to = self.add_influence_frame)
        self.apply_influence_btn.setFixedHeight(50)
        self.apply_influence_btn.clicked.connect(self.apply_influence_to_verts)
        
        back_btn = self.back_button(widget = self.add_influence_frame)
    #===============================================================================================================================#
    #Widget Functions
    #===============================================================================================================================#   
    def change_index(self,index,vtx = None):
        self.function_stack.setCurrentIndex(index)
        self.get_influences()
        if index == 4: pm.softSelect(sse=True,ssf = True)
        else: pm.softSelect(sse=False)
        
    def get_path(self,open = False):
        if open == False:
            path = pm.fileDialog2(fm=3)
            if path != None:
                self.path = path[0]
                self.path_label.setText(self.path)
        else:
            path = ''
            xml_doc = pm.internalVar(userPrefDir=True) + 'weight_for_it_prefs.xml'
            if os.path.exists(xml_doc):
                doc = ET.parse(xml_doc)
                try: path = doc.getroot().find('path').get('id')
                except: pass
            else:
                try:
                    path = sceneName().replace(sceneName().split('/')[-1],'')
                    if os.path.exists(path + 'weights'): path = path + 'weights'
                except: pass
        return path
        
    def refresh_timer(self):
        self.refresher = qc.QTimer()
        self.refresher.setInterval(100)
        self.refresher.timeout.connect(self.refresh_sliders)
        self.refresher.start()
    
    def refresh_sliders(self):
        index = self.function_stack.currentIndex()
        if index == 2 or index == 3:
            [x.vtx_skin_refresh() for x in self.vert_layout.children() if x.__class__.__name__ == 'VertexWeightFrame']
            [x.vtx_skin_refresh() for x in self.average_layout.children() if x.__class__.__name__ == 'VertexWeightFrame']
        elif index == 4:
            self.falloff_slider.hidden_spin.blockSignals(True)
            self.falloff_slider.spin_box.setValue(pm.softSelect(q = True,ssd = True))
            self.falloff_slider.hidden_spin.blockSignals(False)
 
    def back_button(self,widget = None,index = 0):
        if widget != None: back_button = guts.widget_setup(qw.QPushButton('<< Back To Main Menu'),None,add_to = widget)
        else: back_button = guts.widget_setup(qw.QPushButton('<< Back To Main Menu'),None)
        back_button.setFixedHeight(40)
        back_button.clicked.connect(partial(self.change_index,index))
        return back_button

    def save_preferences(self):
        doc_path = '{0}weight_for_it_prefs.xml'.format(pm.internalVar(userPrefDir=True))
        prefs = ET.Element('preferences')
        path = ET.SubElement(prefs,'path')
        path.set('id',self.path)
        guts.publish_xml(prefs,doc_path)
    
    def load_weights(self):
        load_path_weights(self.path)
        
    def save_weights(self):
        if len(pm.ls(sl = True)) > 0:
            for obj in pm.ls(sl = True):
                body = obj.getChildren(s = True)[0]
                skin = []
                skin_info = []
                mesh_connections =  pm.listConnections(obj.getChildren(s = True)[0].inMesh)
                for all in mesh_connections:
                    if all.nodeType() == 'skinCluster': skin = all

                if skin:
                    try:
                        document_path = '{0}/{1}.xml'.format(self.path,obj.name())
                        influences = pm.listConnections(skin.matrix)
                        
                        info = ET.Element(str(obj.name()))
                        bones = ET.SubElement(info,'bones')
                        bones.set('id',str(obj.name()))
                        
                        for influence in influences:
                            bone = ET.SubElement(bones,'joint')
                            bone.set('id',str(influence.name()))
                        
                        mesh = ET.SubElement(info,'mesh')
                        mesh.set('id',str(obj.name()))
                        mesh.set('max_influences',str(skin.maxInfluences.get()))
                        vertices = pm.ls(obj.vtx[:],fl = True)
                        
                        pm.progressWindow(title='Saving...',pr=0, st= obj.replace('_',' ').title() + ': 0%', ii = False)
                        percent = 100.00/float(len(vertices))
                        pm.refresh()
                        
                        for k, vert in enumerate(vertices):
                            progress = percent * (k + 1)
                            pm.progressWindow(e=1, pr=progress, st= obj.replace('_',' ').title() + ': %d%%' % progress)
                            vertex = ET.SubElement(mesh,'vert')
                            vertex.set('id',str(vert.name()))
                            for influence in influences:
                                value = pm.skinPercent(skin,vert,q=True, t = influence, v = True)
                                if value > 0: 
                                    bind_joint = ET.SubElement(vertex,'influence')
                                    bind_joint.set('id',str(influence.name()))
                                    bind_joint.set('value',str(value))
                            pm.refresh()
                            
                        guts.publish_xml(info, document_path)
                    except: pass
                    
                    pm.progressWindow(endProgress=1)
                    pm.refresh()
   
    def closeEvent(self,event):
        self.refresher.stop()
        pm.scriptJob(kill = self.widgets['selection_influences'])
    #===============================================================================================================================#
    #Selection Functions
    #===============================================================================================================================# 
    def get_skin(self,objects = None):
        shape = None
        obj = None
        vtx = None
        skin = None
        if objects == None: objects = pm.ls(sl = True,fl = True)
        
        if len(objects) > 0:
            obj = objects[0]
            if obj.nodeType() == 'transform':
                shape = obj.getShape()
                if shape.nodeType() != 'mesh': shape = None
            elif obj.nodeType() == 'mesh':
                shape = pm.PyNode(str(obj.split('.')[0]))
                obj = shape.getParent()
                vtx = pm.ls(pm.polyListComponentConversion(objects,tv = True),fl = True)

        if shape != None:
            try: skin = pm.listHistory(obj,type = 'skinCluster')[0]
            except: skin = None
        
        return [obj,shape,skin,vtx]
    
    def get_influences(self):
        #Variables
        potentials = pm.ls(type = 'joint')
        current_text = self.widgets['current_filter'].text().replace(' ','_')
        non_text = self.widgets['non_filter'].text().replace(' ','_')
        soft_select_text = self.skinning_filter.text().replace(' ','_')
        vtx_text = self.vtx_filter.text().replace(' ','_')
        self.widgets['current_influences'].clear()
        self.widgets['non_influences'].clear()
        self.vtx_influences.clear()
        self.skin_influences.clear()
        obj, shape, skin, vtx = self.get_skin()
        index = self.function_stack.currentIndex()
        vert_influences = []
        influences = []
        
        if skin != None: influences = pm.listConnections(skin.matrix)
        if index == 1:
            if obj != None:
                for x in influences:
                    if current_text != '':
                        if current_text in x.name(): self.widgets['current_influences'].addItem(x.name())
                    else: self.widgets['current_influences'].addItem(x.name())
                    if x in potentials: potentials.remove(x)
                for x in potentials:
                    if x.endswith('_bind_joint'):
                        if non_text != '':
                            if non_text in x.name(): self.widgets['non_influences'].addItem(x.name())
                        else: self.widgets['non_influences'].addItem(x.name())
        elif index == 2 or index == 3:
            [x.deleteLater() for x in self.vert_layout.children() if x.__class__.__name__ == 'VertexWeightFrame']
            [x.deleteLater() for x in self.average_layout.children() if x.__class__.__name__ == 'VertexWeightFrame']
            if vtx != None and index == 2:
                for v in vtx: frame = guts.widget_setup(VertexWeightFrame([obj,shape,skin,v],self),None,add_to = self.vert_layout)
            elif vtx != None and index == 3:
                frame = guts.widget_setup(VertexWeightFrame([obj,shape,skin,vtx],self,label = 'Selected Vertices'),None,add_to = self.average_layout)
        elif index == 4:
            for x in influences:
                if soft_select_text != '':
                    if soft_select_text in x.name(): self.skin_influences.addItem(x.name())
                else: self.skin_influences.addItem(x.name())
        elif index == 5:
            for x in influences:
                if vtx_text != '':
                    if vtx_text in x.name(): self.vtx_influences.addItem(x.name())
                else: self.vtx_influences.addItem(x.name())
    
    #===============================================================================================================================#
    #Copy Skin Weight Functions
    #===============================================================================================================================#   
    def copy_skin_weights(self):
        objects = pm.ls(sl = True)
        if len(objects) > 1:
            targets = objects[1:]
            primary_obj, shape, skin, vtx = self.get_skin(objects = [objects[0]])
            
            if skin != None:
                joints = pm.listConnections(skin.matrix)
                for target in targets:
                    obj, obj_shape, obj_skin, obj_vtx = self.get_skin(objects = [target])
                    if obj_skin != None: pm.delete(obj_skin)
                    obj_skin = pm.skinCluster(joints,obj,n = obj + '_skin',tsb = True, mi = 4, sm = 1, nw = 1)
                    pm.skinPercent(obj_skin, obj_shape.vtx[:], tv = (joints[0],1.00))
                    pm.copySkinWeights(ss = skin,ds = obj_skin,nm = True, sa = 'closestPoint', ia = ['label','oneToOne','closestJoint'])
        else:
            message = 'You need at least two objects to copy skin weights.\n\nFirst select the skinned object, then select the unskinned objects.'
            err = pm.confirmDialog(t = 'Copy Skin Weights Selection Error',m = message, b = ['Okay'],cb = 'Okay')
    
    def mirror_skin_weights(self):
        objects = pm.ls(sl = True)
        if len(objects) > 0:
            for x in objects:
                obj, shape, skin, vtx = self.get_skin(objects = [x])
                if skin != None:
                    pm.copySkinWeights(ss = skin,ds = skin,mm = 'YZ', sa = 'closestPoint', ia = ['label','oneToOne'])
        else:
            message = 'You need at least one object to mirror skin weights.'
            err = pm.confirmDialog(t = 'Mirror Skin Weights Selection Error',m = message, b = ['Okay'],cb = 'Okay')
    
    def hammer_skin_weights(self):
        obj, shape, skin, vtx = self.get_skin()
        if skin != None and vtx != None: mel.eval('weightHammerVerts;')
        else:
            message = 'You must select vertices, faces, or edges of a skinned mesh to hammer skin weights.'
            err = pm.confirmDialog(t = 'Hammer Skin Weights Selection Error',m = message, b = ['Okay'],cb = 'Okay')
    #===============================================================================================================================#
    #Edit Influence Functions
    #===============================================================================================================================#           
    def add_influences_to_skin(self):
        obj, shape, skin, vtx = self.get_skin()
        if obj != None:
            joints = [pm.PyNode(x.text()) for x in self.widgets['non_influences'].selectedItems()]
            if skin != None: pm.skinCluster(skin,e = True,dr = 8.0, ps = 0, ns = 10,lw = False,wt = 0 ,ai = joints)
            else:
                skin = pm.skinCluster(joints,obj,n = obj + '_skin',tsb = True, mi = 4, sm = 1, nw = 1)
                pm.skinPercent(skin, shape.vtx[:], tv = (joints[0],1.00))
            pm.select(obj)
            self.get_influences()
         
    def remove_influences_from_skin(self):
        obj, shape, skin, vtx = self.get_skin()
        if obj != None:
            joints = [pm.PyNode(x.text()) for x in self.widgets['current_influences'].selectedItems()]
            if skin != None:
                pm.skinCluster(skin,e = True,ri = joints)
                if len(pm.listConnections(skin.matrix)) == 0:
                    pm.delete(skin)
                    pm.refresh()
            pm.select(obj)
            self.get_influences()
    #===============================================================================================================================#
    #Vertex Skin Weight Functions
    #===============================================================================================================================#   
    def apply_influence_to_verts(self):
        obj, shape, skin, _v = self.get_skin()
        values = [(x.text(),0.01) for x in self.vtx_influences.selectedItems()]
        pm.skinPercent(skin,self.change_vertex,tv = values)
        self.change_index(self.previous_index)
        self.get_influences()
    #===============================================================================================================================#
    #Soft Selection Conversion Functions
    #===============================================================================================================================#      
    def convert_soft_selection_to_skinweights(self):
        vertices = self.get_soft_selection_value()
        try: bone = pm.PyNode(self.skin_influences.currentItem().text())
        except: bone = None
        print bone
        obj, shape, skin, vtx = self.get_skin()
        
        if bone != None:
            pm.undoInfo(ock = True)
            pm.polyListComponentConversion(pm.ls(sl = True,fl = True),tv = True)
            for v in vertices: pm.skinPercent(skin, shape.vtx[v],tv = (bone,vertices[v]))
            pm.undoInfo(cck = True)
        else:
            message = 'You first need to select a joint from the list above before converting.'
            err = pm.confirmDialog(t = 'Soft Select Conversion Error',m = message, b = ['Okay'],cb = 'Okay')
    
    def get_soft_selection_value(self):
        val = self.highest_weight.hidden_spin.value()
        if not pm.softSelect(q=True, sse=True): return None
        
        values = {}
        soft_selection = om.MRichSelection()
        try: om.MGlobal.getRichSelection(soft_selection)
        except: pass
        soft_selection_list = om.MSelectionList()
        soft_selection.getSelection(soft_selection_list)
        amnt = soft_selection_list.length()
    
        for x in xrange(amnt):
            shape_dag_path = om.MDagPath()
            shape_object = om.MObject()
            try: soft_selection_list.getDagPath(x, shape_dag_path, shape_object)
            except: pass
            object = om.MFnSingleIndexedComponent(shape_object)
            try:
                for i in xrange(object.elementCount()):
                    weight = object.weight(i)
                    values[object.element(i)] = weight.influence() * val
            except: pass
        
        return values

    def falloff_radius_changed(self):
        value = self.falloff_slider.hidden_spin.value()
        pm.softSelect(ssd = value,sud = 0.5)
#====================================================================================================================#
class AttributeSlider(qw.QFrame):
    def __init__(self,label,value = 0,slider_max = 100,spin_max = 1,frame = False,parent = None):
        super(AttributeSlider,self).__init__(parent)
        
        #Variables
        self.slider_max = slider_max
        self.spin_max = spin_max
        self.current_value = value

        guts.widget_setup(self,qw.QHBoxLayout(),cm = (2,0,2,0),spacing = 5)
        if frame == True: self.setFrameStyle(qw.QFrame.StyledPanel)
        self.setFixedHeight(30)
        title = guts.widget_setup(qw.QLabel(label),None,add_to = self)
        title.setFixedHeight(20)
        
        #Slider
        self.slider = guts.widget_setup(qw.QSlider(qc.Qt.Horizontal),None,add_to = self)
        self.slider.valueChanged.connect(self.slider_value_change)
        self.slider.setMaximum(self.slider_max)
        
        #Spin Box
        self.spin_box = guts.widget_setup(qw.QDoubleSpinBox(),None,add_to = self)
        self.spin_box.setFixedWidth(100)
        self.spin_box.setMaximum(self.spin_max)
        self.spin_box.valueChanged.connect(self.spinbox_value_change)
        self.spin_box.setSingleStep(0.01)
        
        self.hidden_spin = guts.widget_setup(qw.QDoubleSpinBox(),None,add_to = self)
        self.hidden_spin.setValue(value)
        self.hidden_spin.hide()
        
        self.spin_box.setValue(value)
        
    def slider_value_change(self):
        v = float(self.slider.value()/ float(self.slider_max / self.spin_max))
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(v)
        self.spin_box.blockSignals(False)
        self.hidden_spin.setValue(v)
        self.current_value = v
        
    def spinbox_value_change(self):
        v = float(self.spin_box.value())
        self.slider.blockSignals(True)
        self.slider.setValue(v * float(self.slider_max / self.spin_max))
        self.slider.blockSignals(False)
        self.hidden_spin.setValue(v)
        self.current_value = v
#====================================================================================================================#
class LockButton(qw.QPushButton):
    def __init__(self,item,ui,parent = None):
        super(LockButton,self).__init__(parent)
        self.lock = False
        self.lock_value = 0
        self.item = item
        self.ui = ui
        self.slider = self.ui.sliders[item]
        lock_image = '{0}icons/lock.png'.format(pm.internalVar(upd = True))
        unlock_image = '{0}icons/unlock.png'.format(pm.internalVar(upd = True))
        
        self.lock_style = ("QPushButton {background-image: url('" + lock_image + "');"
                          "background-repeat: no-repeat; background-position: center center;"
                          "border-radius: 2px;}")
        
        self.unlock_style = ("QPushButton {background-image: url('" + unlock_image + "');"
                            "background-repeat: no-repeat; background-position: center center;"
                            "border-radius: 2px;}")

        self.setStyleSheet(self.unlock_style)
        self.setFixedSize(30,30)
        self.clicked.connect(self.change_lock)
        
    def change_lock(self):
        val = self.slider.hidden_spin.value()
        if self.lock == False:
            self.lock = True
            self.setStyleSheet(self.lock_style)
            self.ui.max_value -= val
            self.slider.slider.setEnabled(False)
            self.slider.spin_box.setEnabled(False)
        else:
            self.lock = False
            self.setStyleSheet(self.unlock_style)
            self.ui.max_value += val
            self.slider.slider.setEnabled(True)
            self.slider.spin_box.setEnabled(True)
        
        for x in self.ui.sliders:
            sl = self.ui.sliders[x]
            lock_btn = self.ui.locks[x]
            if lock_btn.lock == False:
                slide_val = self.ui.max_value * float(sl.slider_max / sl.spin_max)
                sl.slider.setMaximum(slide_val)
#====================================================================================================================# 
class MinusButton(qw.QPushButton):
    def __init__(self,item,ui,parent = None):
        super(MinusButton,self).__init__(parent)
        self.item = item
        self.ui = ui
        
        self.setFixedSize(30,30)
        minus_image = '{0}icons/minus.png'.format(pm.internalVar(upd = True))
        self.setStyleSheet("QPushButton {background-image: url('" + minus_image + "');"
                           "background-repeat: no-repeat; background-position: center center;"
                           "border-radius: 2px;}")
        self.clicked.connect(self.remove_influence)
        
    def remove_influence(self):
        self.ui.sliders[self.item].spin_box.setValue(0)
        self.ui.sliders[self.item].deleteLater()
        self.ui.locks[self.item].deleteLater()
        self.deleteLater()
        del self.ui.sliders[self.item]
        del self.ui.locks[self.item]
        del self.ui.minus[self.item]
        self.ui.setFixedHeight(90 + (30 * len(self.ui.sliders)))
#====================================================================================================================#
class VertexWeightFrame(qw.QFrame):
    '''Based on the tool by Robert Joosten (https://vimeo.com/120942200)'''
    def __init__(self,data,ui,label = '',parent = None):
        super(VertexWeightFrame,self).__init__(parent)
        
        #Variables
        self.sliders = {}
        self.locks = {}
        self.minus = {}
        self.max_value = 1.000
        self.ui = ui
        
        #Setup
        guts.widget_setup(self,qw.QVBoxLayout(),cm = (2,2,2,2),spacing = 2)
        self.setStyleSheet('QFrame {background-color: rgb(80,80,80);}')
        self.setFixedHeight(90)
        
        self.influences = []
        self.obj, self.shape, self.skin, self.vtx = data
        if self.skin != None: self.influences = pm.listConnections(self.skin.matrix)
        
        if label == '': label = str(self.vtx)
        
        self.title = guts.widget_setup(qw.QLabel(label),None,add_to = self)
        self.title.setStyleSheet('QLabel {font-weight: bold; font-size: 12pt;}')
        self.title.setFixedHeight(30)

        if not isinstance(self.vtx,list): self.vtx = [self.vtx]
        if self.vtx != None:
            self.attribute_area = guts.widget_setup(qw.QWidget(),qw.QGridLayout(),spacing = 2,add_to = self)
            self.setup_attribute_sliders()
            self.add_btn = guts.widget_setup(qw.QPushButton('Add Influences'),None,add_to = self)
            self.add_btn.setFixedHeight(35)
            self.add_btn.clicked.connect(self.change_apply_btn)
            
    def change_apply_btn(self):
        verts = self.vtx
        if not isinstance(verts,list): verts = [verts]
        self.ui.change_vertex = verts
        self.ui.previous_index = self.ui.function_stack.currentIndex()
        self.ui.change_index(5)
    
    def get_influences(self):
        vert_influences = []
        vert_data = {}
        all_values = []
        
        if self.vtx != None and len(self.influences) > 0:
            for v in self.vtx:
                values = pm.skinPercent(self.skin,v,q = True,v = True)
                current_values = []
                for i, val in enumerate(values):
                    if round(val,2) >= 0.01:
                        vert_influences.append(self.influences[i])
                        current_values.append(val)
                all_values.append(current_values)
            
            if len(self.vtx) > 1: vert_influences = list(set([x for x in vert_influences if vert_influences.count(x) == len(self.vtx)]))
            
            for i in range(len(vert_influences)):
                average = 0
                for val in all_values: average += val[i]
                vert_data[str(vert_influences[i].name())] = round((average / len(self.vtx)),2)
        
        return vert_data
        
    def setup_attribute_sliders(self):
        vert_data = self.get_influences()
        for i, x in enumerate(vert_data):
            val = vert_data[x]
            self.sliders[x] = guts.widget_setup(AttributeSlider(x,value = val,frame = True),None,add_to = [self.attribute_area,i,2])
            self.locks[x] = guts.widget_setup(LockButton(x,self),None,add_to = [self.attribute_area,i,0])
            self.minus[x] = guts.widget_setup(MinusButton(x,self),None,add_to = [self.attribute_area,i,1])
        for x in self.sliders:
            self.sliders[x].hidden_spin.valueChanged.connect(partial(self.balance_the_weights,x))
        self.setFixedHeight(90 + (30 * len(vert_data)))
        
    def balance_the_weights(self,slider,*args):
        val = self.sliders[slider].hidden_spin.value()
        percent_left = self.max_value - val
        o_val = 0.000
        values = [(slider,val)]
        
        for x in self.sliders:
            if x != slider:
                self.sliders[x].hidden_spin.blockSignals(True)
                if self.locks[x].lock == False: o_val += self.sliders[x].hidden_spin.value()
                
        for x in self.sliders:
            if x != slider and self.locks[x].lock != True:
                try: v = round(((self.sliders[x].hidden_spin.value() * percent_left) / o_val ),2)
                except: v = 0.01
                self.sliders[x].spin_box.setValue(v)
                values += [(x,v)]
                
        for x in self.sliders: self.sliders[x].hidden_spin.blockSignals(False)
        pm.skinPercent(self.skin,self.vtx,tv = values)
        
    def vtx_skin_refresh(self):
        for x in self.sliders: self.sliders[x].hidden_spin.blockSignals(True)
        for x in self.sliders:
            val = round(pm.skinPercent(self.skin,self.vtx,transform = x,q = True),2)
            if val != self.sliders[x].current_value:
                self.sliders[x].spin_box.setValue(pm.skinPercent(self.skin,self.vtx,transform = x,q = True))
        for x in self.sliders: self.sliders[x].hidden_spin.blockSignals(False)    
#====================================================================================================================#
#WeightList()