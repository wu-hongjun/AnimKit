import pymel.all as pm
import maya.cmds as mc
import MARS as mars
import MARS.MarsUtilities as mu
import gui.GuiUtilities as guts
from gui.Meta_Marking_Menu import mars_component_rerun
from functools import partial
import maya, os, shutil, subprocess
import maya.mel as mel
import xml.etree.ElementTree as ET
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg
reload(mars)
reload(mu)
reload(guts)
#===============================================================#
import platform
PLAT = str(platform.system())

if "Darwin" in PLAT:
    USER = os.environ["HOME"]
    DESKTOP = os.path.expanduser("~/Desktop")
else:
    USER = os.getenv("USERPROFILE").replace('\\','/')
    DESKTOP = USER + '/Desktop'


INDEX = 0
FOLDER = DESKTOP + "/capstone_scripts/"
LIBRARY = FOLDER + 'pose_library'
SHOTS = FOLDER + 'assets/shot/'
XML_DOC = LIBRARY + '/pose_library.xml'
#===============================================================#
class DragTabButton(qw.QPushButton):
    def __init__(self,text,tab,parent = None):
        super(DragTabButton,self).__init__(parent)
        self.setText(text.replace('_',' ').title())
        
        self.tab = tab
        self.setFixedHeight(40)
        self.text = text
        self.mimeText = self.text
        self.type = tab.type
        
    '''def mouseMoveEvent(self, event):
        mimeData = qc.QMimeData()
        mimeData.setText(self.mimeText)
        self.drag = qg.QDrag(self)
        self.drag.setMimeData(mimeData)
        self.drag.exec_(qc.Qt.CopyAction | qc.Qt.MoveAction)'''
#===============================================================#
class AnimationTab(qw.QFrame):
    widgets = {}
    def __init__(self,asset,ui,parent = None):
        super(AnimationTab,self).__init__(parent)
        self.opened = False
        self.new_image = False
        
        self.ui = ui
        self.asset = asset
        self.asset_name = asset.get('name')
        self.name = self.asset_name.replace('_',' ').title()
        self.type = asset.get('type')
        self.path = asset.get('path')
        self.doc = '{0}{1}.xml'.format(self.path, self.type)
        thumb = '{0}.icon.png'.format(self.path)
        
        self.setFixedHeight(59)
        guts.widget_setup(self,qw.QVBoxLayout(),spacing = 2,add_to = self.ui.asset_layout)
        self.setFrameStyle(qw.QFrame.StyledPanel)

        #Closed Grid
        self.top_grid = guts.widget_setup(qw.QWidget(),qw.QGridLayout(),spacing = 5,add_to = self)
        self.top_grid.setFixedHeight(55)

        ##Thumbnail
        self.thumbnail = guts.widget_setup(qw.QPushButton(),None,add_to = [self.top_grid,0,0])
        self.thumbnail.setFixedSize(55,55)
        self.thumbnail.setStyleSheet("QPushButton {background-image: url('" + self.path + "/.icon.png');"
                                     "background-repeat: no-repeat; background-position: center center;"
                                     "border-radius: 2px;}")

        ##Tab Button
        self.create_tab_button()
        
        ##Updated
        time = '{0}\n{1}'.format(self.asset.get('day'),self.asset.get('time'))
        self.update = guts.widget_setup(guts.center_label(time,None),None,add_to = [self.top_grid,0,2])
        self.update.setFixedWidth(75)
    #=====================================================================================================================#
    def create_tab_button(self):
        try:
            old_btn = self.tab_button
            old_text = old_btn.text
            old_btn.deleteLater()
        except: pass
        
        self.tab_button = guts.widget_setup(DragTabButton(self.name,self),None,add_to = [self.top_grid,0,1])
        self.tab_button.setFixedHeight(55)
        self.tab_button.setStyleSheet('QPushButton{background-color: grey;}')
        if self.type == 'clip': self.tab_button.setStyleSheet('QPushButton{background-color: teal;}')
        self.tab_button.clicked.connect(self.open_tab)
    
    def open_tab(self):
        tabs = [x for x in self.ui.asset_layout.children() if x.__class__.__name__ == 'AnimationTab']
        height = self.height()
        for tab in tabs:
            if tab.height() == 320:
                tab.setFixedHeight(59)
                tab.tab_menu.deleteLater()
                if tab.type == 'clip': tab.refresher.deleteLater()
                
        if height == 59:
            self.setFixedHeight(320)
            self.tab_menu = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = 5,cm = (5,5,5,5),add_to = self)
            
            self.icon = guts.widget_setup(qw.QFrame(),None,add_to = self.tab_menu)
            self.icon.setFrameStyle(qw.QFrame.StyledPanel)
            self.icon.setStyleSheet("QFrame {background-image: url('" + self.path + "/.image.png');}")
            self.icon.setFixedSize(250,250)
            
            self.button_area = guts.widget_setup(qw.QStackedWidget(),None,add_to = self.tab_menu)
            self.button_area.setFixedHeight(250)
            self.main_tab_button_setup()
            self.apply_button_setup()
            self.rename_button_setup()
            self.update_image_button_setup()
            
            if self.type == 'clip':
                self.refresher = qc.QTimer()
                self.refresher.setInterval(100)
                self.refresher.timeout.connect(self.import_frame_change)
                self.refresher.start()
            
    def change_tab(self,index = 0):
        self.button_area.setCurrentIndex(index)
        if self.type == 'clip':
            if index == 1: self.refresher.start()
            else: self.refresher.stop()
        
    def back_tab_button(self):
        btn = qw.QPushButton('<< Back')
        btn.setFixedHeight(40)
        btn.clicked.connect(self.change_tab)
        return btn
        
    def delete_asset(self):
        message = 'You are about to permanantly delete this pose/animation.\nAre you sure you wish to proceed?'
        confirm = pm.confirmDialog(t = 'WARNING:',m = message,b = ['Yes','No'],cb = 'No')
        if confirm == 'Yes':
            doc = ET.parse(XML_DOC)
            root = doc.getroot()
            production = root.findall('Production')[INDEX]
            asset = production.find('Asset[@name="{0}"][@type="{1}"]'.format(self.name.replace(' ','_').lower(),self.type))
            path = '{0}{1}s/{2}'.format(production.get('path'),asset.get('type'),asset.get('name'))
            production.remove(asset)
            guts.publish_xml(root,XML_DOC)
            self.ui.get_poses_and_clips()
            shutil.rmtree(path)
    
    def open_folder(self):
        os.startfile(self.path.replace('/','\\'))
    #=====================================================================================================================#
    def main_tab_button_setup(self):
        button_menu = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (2,0,0,2),add_to = self.tab_menu) 
        self.button_area.addWidget(button_menu)
        
        btns = ['apply_{0}'.format(self.type),'rename_asset','update_image','open_folder','delete_asset']
        for btn in btns:
            btn_txt = btn.replace('_',' ').title().replace('Xml','XML')
            self.widgets[btn] = guts.widget_setup(qw.QPushButton(btn_txt),None,add_to = button_menu)
            self.widgets[btn].setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
            
        #Functions
        self.widgets['apply_{0}'.format(self.type)].clicked.connect(partial(self.change_tab,1))
        self.widgets['rename_asset'].clicked.connect(partial(self.change_tab,2))
        self.widgets['update_image'].clicked.connect(partial(self.change_tab,3))
        self.widgets['delete_asset'].clicked.connect(self.delete_asset)
        self.widgets['open_folder'].clicked.connect(self.open_folder)
    #=====================================================================================================================#
    def apply_button_setup(self):
        button_menu = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (2,0,0,2),add_to = self.tab_menu) 
        self.button_area.addWidget(button_menu)
        
        chars = ['Characters']
        chars += [x.tag for x in self.asset.find('Characters').findall('*')]
        self.character_combo = guts.center_combobox(items = chars, widget = button_menu)
        self.character_combo.setFixedHeight(25)
        
        apply_area = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = button_menu)
        apply_options = {'apply_to':['all_anims','selected_anims'],'import':['normal','mirrored'],
                         'with':['no_buffer','buffer'],'key_pose':['no','yes']}
        items = ['apply_to','import','with']
        if self.type == 'pose': items = ['apply_to','import','key_pose']
        
        for y in items:
            option_area = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),cm = (5,5,5,5),spacing = 5,add_to = apply_area)
            option_area.setFrameStyle(qw.QFrame.StyledPanel)
            option_area.setFixedHeight(30)
            guts.widget_setup(qw.QLabel('{0}: '.format(y.replace('_',' ').title())),None,add_to = option_area)
            for x in apply_options[y]:
                self.widgets['{0}_{1}'.format(y,x)] = guts.widget_setup(qw.QRadioButton(x.replace('_',' ').title()),None,add_to = option_area)
            self.widgets['{0}_{1}'.format(y,apply_options[y][0])].setChecked(True)
        
        btn_txt = 'Apply'
        if self.type == 'clip': btn_txt = 'Apply At {0}'.format(pm.currentTime())
        self.apply_btn = guts.widget_setup(qw.QPushButton(btn_txt),None,add_to = apply_area)
        self.apply_btn.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
        self.apply_btn.clicked.connect(self.apply_pose_or_clip)
    
        back_btn = guts.widget_setup(self.back_tab_button(),None,add_to = button_menu)
    
    def import_frame_change(self):
        self.apply_btn.setText('Apply At {0}'.format(pm.currentTime()))
    
    def apply_pose_or_clip(self):
        char_setting = self.character_combo.currentText()
        doc = ET.parse(self.doc)
        root = doc.getroot()
        characters = root.findall('Character')
        original_selection = [x for x in pm.ls(sl = True) if x.hasAttr('animNode')]
        real_rigs = list(set([guts.get_root_rig(x) for x in guts.rig_check()]))
        ref_name = [x.name().split(':')[0] for x in real_rigs][0]
        
        pm.undoInfo(ock = True)
        if len(original_selection) > 0:
            for xml_char in characters:
                if xml_char.get('rig') == char_setting or char_setting == 'Characters':
                    for xml_anim in xml_char.findall('Anim'):
                        buffer = pm.currentTime(q = True) - 1
                        if self.type == 'clip' and self.widgets['with_no_buffer'].isChecked():
                            buffer = pm.currentTime(q = True) - guts.string_value_conversion(xml_char.get('min'))
                        
                        try: anim = pm.PyNode(xml_anim.get('name'))
                        except: anim = pm.PyNode(ref_name + ':' + xml_anim.get('name'))
                        
                        if self.widgets['import_mirrored'].isChecked():
                            side = xml_anim.get('side')
                            new_side = 'center'
                            if side == 'left': new_side = 'right'
                            elif side == 'right': new_side = 'left'
                            anim = pm.PyNode(xml_anim.get('name').replace(side,new_side))
                        
                        for xml_attr in xml_anim.findall('Attribute'):
                            attribute = pm.Attribute('{0}.{1}'.format(anim,xml_attr.get('id')))
                            
                            for xml_key in xml_attr.findall('Key'):
                                if self.widgets['apply_to_all_anims'].isChecked() or anim in original_selection:
                                    frame = guts.string_value_conversion(xml_key.get('frame'))
                                    value = guts.string_value_conversion(xml_key.get('value'))
                                    if self.type == 'pose':
                                        try: 
                                            if self.widgets['key_pose_no'].isChecked(): attribute.set(value)
                                            else: pm.setKeyframe(attribute,v = value,time = (pm.currentTime(q = True)))
                                        except: print attribute
                                    else:
                                        t = frame + buffer
                                        iw = guts.string_value_conversion(xml_key.get('iw'))
                                        ow = guts.string_value_conversion(xml_key.get('ow'))
                                        ia = guts.string_value_conversion(xml_key.get('ia'))
                                        oa = guts.string_value_conversion(xml_key.get('oa'))
                                        pm.setKeyframe(attribute,v = value,time = (t))
                                        pm.keyTangent(attribute,lock = False,e = True, time = (t),ia = ia, iw = iw, oa = oa, ow = ow)
                                        pm.keyTangent(attribute,lock = False,e = True,time = (t), itt = xml_key.get('itt'), ott = xml_key.get('ott'))
            pm.undoInfo(cck = True)
            self.change_tab()
        else:
            message = "You need to select a character rig's anim to proceed."
            error = pm.confirmDialog(t = 'ERROR: Rig Not Selected',m = message,b = ['Okay'],cb = 'Okay')
    #=====================================================================================================================#        
    def rename_button_setup(self):
        button_menu = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (2,0,0,2),add_to = self.tab_menu) 
        self.button_area.addWidget(button_menu)
        
        #Name Area
        name_area = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),cm = (5,5,5,5),spacing = 5,add_to = button_menu)
        name_area.setFrameStyle(qw.QFrame.StyledPanel)
        name_area.setFixedHeight(50)
        
        guts.widget_setup(qw.QLabel('New Name:'),None,add_to = name_area)
        self.new_name = guts.widget_setup(qw.QLineEdit(),None,add_to = name_area)
        
        #Buttons
        apply_btn = guts.widget_setup(qw.QPushButton('Apply New Name'),None,add_to = button_menu)
        apply_btn.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
        apply_btn.clicked.connect(self.rename_asset)
        
        back_btn = guts.widget_setup(self.back_tab_button(),None,add_to = button_menu)
        
    def rename_asset(self):
        new_name = self.new_name.text().replace(' ','_')
        if new_name not in ['','_']:
            new_path = self.path.replace(self.asset_name,new_name)
            
            #Correct XML
            doc = ET.parse(XML_DOC)
            root = doc.getroot()
            production = root.findall('Production')[INDEX]
            asset = production.find('Asset[@path="{0}"]'.format(self.path))
            asset.set('path',new_path)
            asset.set('name',new_name)
            guts.publish_xml(root,XML_DOC)
            
            #Rename the Pathes
            os.rename(self.path,new_path)
            
            #Fix The Variables
            self.tab_button.setText(new_name.replace('_',' ').title())
            self.doc = self.doc.replace(self.asset_name,new_name)
            self.path = new_path
            self.asset_name = new_name
            
            self.change_tab()
    #=====================================================================================================================# 
    def update_image_button_setup(self):
        button_menu = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (2,5,0,2),add_to = self.tab_menu) 
        self.button_area.addWidget(button_menu)
        
        directions = 'DIRECTIONS:\n\n1.) Press "Take Picture."\n\n2.) Repeat until positioning is correct.\n\n3.) Press "Save Image" when done.'
        guts.center_label(directions,widget = button_menu)
        
        btns = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = 5, add_to = button_menu)
        for x in ['take_picture','save_image']:
            self.widgets[x] = guts.widget_setup(qw.QPushButton(x.replace('_',' ').title()),None,add_to = btns)
            self.widgets[x].setFixedHeight(60)
            
        self.widgets['take_picture'].clicked.connect(self.take_picture)
        self.widgets['save_image'].clicked.connect(self.save_image)
        
        back_btn = guts.widget_setup(self.back_tab_button(),None,add_to = button_menu)
        
    def take_picture(self):
        temp_icon, temp_path = guts.viewport_image((250,250),(40,40))
        self.new_image = True
        self.icon.setStyleSheet('background-image: url(' + temp_path + ');' +
                                'background-repeat: no-repeat; background-position: center center;')
                                 
    def save_image(self):
        if self.new_image == True:
            temp_icon = pm.internalVar(userPrefDir=True) + '/temp_icon.png'
            temp_image = pm.internalVar(userPrefDir=True) + '/temp_image.png'
            os.remove(self.path + '.icon.png')
            os.remove(self.path + '.image.png')
            shutil.move(temp_icon,self.path + '.icon.png')
            shutil.move(temp_image,self.path + '.image.png')
            self.icon.setStyleSheet("QFrame {background-image: url('" + self.path + "/.image.png');}")
            self.thumbnail.setStyleSheet("QPushButton {background-image: url('" + self.path + "/.icon.png');"
                                         "background-repeat: no-repeat; background-position: center center;"
                                         "border-radius: 2px;}")
            self.change_tab()
#===============================================================#
class CorrectiveFrame(qw.QFrame):
    widgets = {}
    def __init__(self,title,ui,parent = None):
        super(CorrectiveFrame,self).__init__(parent)
        
        self.component = title
        self.ui = ui
        self.type = 'MultiConstraint'
        
        guts.widget_setup(self,qw.QHBoxLayout(),cm = (2,2,2,2),spacing = 5)
        self.setFrameStyle(qw.QFrame.StyledPanel)
        self.setFixedHeight(40)
        
        guts.widget_setup(qw.QLabel(title),None,add_to = self)
        
        if 'FKIK' in title:
            self.type = 'FKIK'
            items = ['FK Mode','IK Mode']
        else: items = pm.attributeQuery('parent_to',n = title,le = True)[0].split(':')
        
        self.combo = guts.center_combobox(items = items,widget = self)
        self.combo.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Fixed)
        self.combo.setFixedHeight(30)
        
        close_button = guts.widget_setup(qw.QPushButton('X'),None,add_to = self)
        close_button.setFixedSize(30,30)
        close_button.clicked.connect(self.remove_frame)
        
    def remove_frame(self):
        self.ui.corrective_components.remove(self.component)
        self.ui.get_corrective_components()
        self.deleteLater()

#===============================================================#
class PuppetMaster(qw.QDialog):
    widgets = {}
    def __init__(self,parent = guts.get_main_window()):
        super(PuppetMaster,self).__init__(parent)
        
        ##Checks if PySide window Exists##
        if pm.window('PuppetMaster',ex=True) == True: pm.deleteUI('PuppetMaster',wnd=True)
        
        #Window Setup
        self.corrective_components = []
        self.setObjectName('PuppetMaster')
        self.setWindowTitle('Puppet Master')
        self.setWindowFlags(qc.Qt.Tool)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        guts.widget_setup(self,qw.QHBoxLayout(),cm = (5,5,5,5),spacing = 5)
        self.setMinimumSize(700,400)
        
        #Button Frame
        button_frame = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),spacing = 5,add_to = self)
        button_frame.setFixedWidth(150)
        buttons = ['main_menu','save_pose_or_clip','correct_motion','mirror_animation','open_character_picker']
        for i, btn in enumerate(buttons):
            txt = btn.replace('_',' ').title().replace('Ik','IK').replace('Fk','FK')
            self.widgets[btn] = guts.widget_setup(qw.QPushButton(txt),None,add_to = button_frame)
            self.widgets[btn].setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
        
        #Function Stack
        self.function_stack = guts.widget_setup(qw.QStackedWidget(),None,add_to = self)
        self.main_menu_setup()
        self.save_pose_clip_setup()
        self.correct_motion_setup()
        
        #Functions
        self.widgets['selection_components'] = pm.scriptJob( e= ["SelectionChanged",self.get_corrective_components])
        self.widgets['main_menu'].clicked.connect(partial(self.change_index,0))
        self.widgets['save_pose_or_clip'].clicked.connect(partial(self.change_index,1))
        self.widgets['correct_motion'].clicked.connect(partial(self.change_index,2))
        self.widgets['open_character_picker'].clicked.connect(self.open_character_picker)
        self.resize(700,400)
        self.show()
        
    #====================================================================================================================#     
    #Widget Functions
    #====================================================================================================================#  
    def change_index(self,index = 0):
        self.function_stack.setCurrentIndex(index)
        self.corrective_components = []
        [x.deleteLater() for x in self.correction_scroll.children() if x.__class__.__name__ == 'CorrectiveFrame']
        if index == 0: self.get_poses_and_clips()
        elif index == 1: self.refresh_settings()
        elif index == 2: self.get_corrective_components()
        
    def back_button(self):
        btn = qw.QPushButton('<< Back to Main Menu')
        btn.clicked.connect(self.change_index)
        btn.setFixedHeight(40)
        return btn
        
    def open_character_picker(self):
        from gui.Meta_Character_Picker import MetaCharacterPicker
        meta = MetaCharacterPicker()
    
    def timeline_data(self,name,widget):
        timeline_area = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 5,cm = (5,5,5,5),add_to = widget.layout())
        timeline_area.setFrameStyle(qw.QFrame.StyledPanel)
        timeline_area.setFixedHeight(35)
        
        for x in ['start','end']:
            txt = '{0}_{1}'.format(name, x)
            self.widgets['{0}_check'.format(txt)] = guts.widget_setup(qw.QCheckBox(x.title() + ': '),None,add_to = timeline_area)
            self.widgets[txt] = guts.widget_setup(qw.QSpinBox(),None,add_to = timeline_area)
            self.widgets[txt].setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Fixed)
            self.widgets[txt].setMinimum(-100000)
            self.widgets[txt].setMaximum(100000)
            self.widgets['{0}_check'.format(txt)].stateChanged.connect(partial(self.timeline_turnoff,txt))
            self.timeline_turnoff(txt)
        
        self.widgets['{0}_start'.format(name)].setValue(pm.playbackOptions(min = True, q = True))
        self.widgets['{0}_end'.format(name)].setValue(pm.playbackOptions(max = True, q = True))
        self.widgets['{0}_range_btn'] = guts.widget_setup(qw.QPushButton('Get Timeline Selection Range'),None,add_to = widget)
        self.widgets['{0}_range_btn'].setFixedHeight(30)
        self.widgets['{0}_range_btn'].clicked.connect(partial(self.timeline_range_get,name))
        
        return timeline_area, self.widgets['{0}_range_btn']
    
    def timeline_turnoff(self,name,*args):
        if self.widgets['{0}_check'.format(name)].isChecked(): self.widgets[name].setEnabled(True)
        else: self.widgets[name].setEnabled(False)
    
    def timeline_range_get(self,name,*args):
        maya_timeline = mel.eval('$tmpVar=$gPlayBackSlider')
        range = pm.timeControl(maya_timeline, q = True, ra = True)
        if range[1] - range[0] <= 1: range = [pm.playbackOptions(min = True, q = True),pm.playbackOptions(max = True, q = True)]
        for i, x in enumerate(['start','end']):
            self.widgets['{0}_{1}_check'.format(name,x)].setChecked(True)
            self.widgets['{0}_{1}'.format(name,x)].setValue(range[i])
    
    def closeEvent(self,event):
        pm.scriptJob(kill = self.widgets['selection_components'])
    #====================================================================================================================#
    #Main Menu Functions
    #====================================================================================================================# 
    def main_menu_setup(self):
        frame = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.function_stack.addWidget(frame)
        
        #Filter Settings
        filter_frame = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),cm = (2,2,2,2),spacing = 2,add_to = frame)
        filter_frame.setFrameStyle(qw.QFrame.StyledPanel)
        filter_frame.setFixedHeight(33)
        
        ##Radio Buttons
        radio_buttons = guts.widget_setup(qw.QFrame(),qw.QGridLayout(),cm = (2,2,2,2),spacing = 5,add_to = filter_frame)
        for i, item in enumerate(['all','pose','clip']):
            self.widgets[item + '_btn'] = guts.widget_setup(qw.QRadioButton(item.title()),None,add_to = [radio_buttons,0,i])
            self.widgets[item + '_btn'].clicked.connect(self.get_poses_and_clips)
        self.widgets['all_btn'].setChecked(True)
        self.search = guts.widget_setup(qw.QLineEdit(),None,add_to = filter_frame)
        search_btn = guts.widget_setup(qw.QPushButton('Search'),None,add_to = filter_frame)
        self.search.setFixedHeight(25)
        search_btn.setFixedSize(50,23)
        
        ####Assets
        asset_label_grid = guts.widget_setup(qw.QWidget(),qw.QGridLayout(),add_to = frame)
        for i, all in enumerate(['Icon','Pose / Clip','Updated']):
            l = guts.widget_setup(guts.center_label(all,None),None,add_to = [asset_label_grid,0,i])
            if all == 'Icon': l.setFixedWidth(62)
            elif all == 'Updated': l.setFixedWidth(95)
            l.setFixedHeight(20)
        
        ####Scroll
        assets = guts.widget_setup(qw.QScrollArea(),None,add_to = frame)
        assets.setWidgetResizable(True)
        self.asset_layout = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout())
        self.asset_layout.layout().setAlignment(qc.Qt.AlignTop)
        assets.setWidget(self.asset_layout)
        
        #Functions
        self.get_poses_and_clips()
        self.search.returnPressed.connect(self.get_poses_and_clips)
        search_btn.clicked.connect(self.get_poses_and_clips)
    
    def get_poses_and_clips(self):
        total_search = 'Asset'
        search_text = self.search.text()
        if self.widgets['all_btn'].isChecked() == False:
            if self.widgets['pose_btn'].isChecked() == True: total_search += '[@type="pose"]'
            else: total_search += '[@type="clip"]'
        
        #Clear Assets
        [x.deleteLater() for x in self.asset_layout.children() if x.__class__.__name__ == 'AnimationTab']
        
        #Create Animation Tabs
        doc = ET.parse(XML_DOC)
        root = doc.getroot()
        production = root.findall('Production')[INDEX]
        assets = production.findall(total_search)
        [AnimationTab(asset,self) for asset in assets if search_text == '' or search_text in asset.get('name')]
    
    #====================================================================================================================#    
    #Correctional Motion Functions
    #====================================================================================================================#
    def correct_motion_setup(self):
        frame = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.function_stack.addWidget(frame)
        
        setup_widget = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 5,add_to = frame)
        
        #List Area
        list_area = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = setup_widget)
        list_area.setFixedWidth(150)
        
        #Type
        self.motion_combo = guts.center_combobox(items = ['FKIK Components','MultiConstraints'], widget = list_area)
        self.motion_combo.setFixedHeight(30)
        self.motion_combo.currentIndexChanged.connect(self.get_corrective_components)
        
        #Apply Button
        add_button = guts.widget_setup(qw.QPushButton('>>'),None,add_to = setup_widget)
        add_button.setSizePolicy(qw.QSizePolicy.Fixed,qw.QSizePolicy.Expanding)
        add_button.clicked.connect(self.apply_bake_components)
        add_button.setFixedWidth(25)
        
        #Lists Items to Bake
        self.component_list = guts.widget_setup(qw.QListWidget(),None,add_to = list_area)
        self.component_list.setSelectionMode(qw.QAbstractItemView.ExtendedSelection)
        
        #Button section
        button_section = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = setup_widget)
        
        ###Scroll Section
        corrective_area = guts.widget_setup(qw.QScrollArea(),None,add_to = button_section)
        corrective_area.setWidgetResizable(True)
        self.correction_scroll = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 2)
        self.correction_scroll.layout().setAlignment(qc.Qt.AlignTop)
        corrective_area.setWidget(self.correction_scroll)
        
        #Bake Timeline
        timeline_area, timeline_btn = self.timeline_data('bake',widget = button_section)
        
        #Bake Button
        bake_button = guts.widget_setup(qw.QPushButton('Correct Animation'),None,add_to = button_section)
        bake_button.clicked.connect(self.correct_motion)
        bake_button.setFixedHeight(50)
        
        back_btn = guts.widget_setup(self.back_button(),None,add_to = frame)
        
    def apply_bake_components(self):
        items = [x for x in self.component_list.selectedItems()]
        for i, item in enumerate(items):
            guts.widget_setup(CorrectiveFrame(str(item.text()),self),None,add_to = self.correction_scroll)
            self.component_list.takeItem(self.component_list.row(item))
        self.corrective_components = [x.component for x in self.correction_scroll.children() if x.__class__.__name__ == 'CorrectiveFrame']
        self.get_corrective_components()
    
    def get_corrective_components(self):
        if self.function_stack.currentIndex() == 2:
            self.component_list.clear()
            type = self.motion_combo.currentText()
            rigs = list(set([guts.get_root_rig(x) for x in guts.rig_check()]))
            for rig in rigs:
                char = mars.CharacterRig('','',node = rig)
                if type == 'FKIK Components': comps = [x for x in char.get_complete_rig_components() if 'FKIK' in x.node_type.get()]
                else: comps = [x for x in char.get_complete_rig_anims() if x.hasAttr('parent_to')]
                [self.component_list.addItem(str(x.split(':')[-1])) for x in comps if x not in self.corrective_components]    
    
    def correct_motion(self):
        try: corrective_components = [(pm.PyNode(x.component),x.type,x.combo.currentIndex()) for x in self.correction_scroll.children() if x.__class__.__name__ == 'CorrectiveFrame']
        except: corrective_components = []
        pm.undoInfo(ock = True)
        pm.refresh(su = True)
        
        for comp in corrective_components:
            c , type , index = comp
            if type == 'MultiConstraint':
                keys, key_values = self.get_anim_keys(c,'clip',type = 'bake')
                for key in keys:
                    pm.currentTime(key)
                    mu.constraint_switch(c,index,align = True)
                    pm.setKeyframe(c,time = (key))
                pm.filterCurve(c)
            else:
                component = mars_component_rerun(pm.PyNode(c))
                switch = component.get_switch()
                anims = component.get_IK_anims()
                anims += component.get_FK_anims()
                anims += [switch]
                keys = []
                for anim in anims:
                    k, kv = self.get_anim_keys(anim,'clip',type = 'bake')
                    keys += k
                keys = list(set(keys))
                
                if index == 1:
                    new_keys = []
                    for i ,key in enumerate(keys[:-1]):
                        diff = (keys[i + 1] - key)/4.000
                        for x in range(1,4): new_keys += [(key + round(diff * x))]
                    keys += new_keys
                    keys = sorted(list(set(keys)))
                
                for key in keys:
                    pm.currentTime(key)
                    if index == 0: component.IK_to_FK_switch()
                    else: component.FK_to_IK_switch()
                    pm.setKeyframe(anims,time = (key))
                pm.filterCurve(anims)
                
        pm.refresh(su = False) 
        pm.undoInfo(cck = True)
        [x.deleteLater() for x in self.correction_scroll.children() if x.__class__.__name__ == 'CorrectiveFrame']
    #====================================================================================================================#    
    #Saving Pose or Clip Functions
    #====================================================================================================================#    
    def save_pose_clip_setup(self):
        frame = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.function_stack.addWidget(frame)
        
        setup_widget = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 5,add_to = frame)
        setup_widget.setFixedHeight(250)
        
        #Icon
        self.icon = guts.widget_setup(qw.QFrame(),None,add_to = setup_widget)
        self.icon.setFrameStyle(qw.QFrame.StyledPanel)
        self.icon.setFixedSize(250,250)
        
        #Button Frame
        button_frame = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),spacing = 5,add_to = setup_widget)
        
        ##Name
        label_widget = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 5,cm = (5,5,5,5),add_to = button_frame)
        label_widget.setFrameStyle(qw.QFrame.StyledPanel)
        guts.widget_setup(qw.QLabel('Name: '),None,add_to = label_widget)
        self.pose_clip_name = guts.widget_setup(qw.QLineEdit(),None,add_to = label_widget)
        
        radios = {'type':['pose','clip'],'save':['all_anims','selected_anims']}
        for r in ['type','save']:
            c_frame = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),spacing = 5,cm = (5,5,5,5),add_to = button_frame)
            c_frame.setFrameStyle(qw.QFrame.StyledPanel)
            c_frame.setFixedHeight(30)
            guts.widget_setup(qw.QLabel('{0}: '.format(r.title())),None,add_to = c_frame)
            for x in radios[r]: self.widgets[x] = guts.widget_setup(qw.QRadioButton(x.replace('_',' ').title()),None,add_to = c_frame)
            self.widgets[radios[r][0]].setChecked(True)
        
        self.timeline_area, self.timeline_btn = self.timeline_data('clip',widget = button_frame)
        self.turn_off_timeline()
        
        #Picture Button
        picture_btn = guts.widget_setup(qw.QPushButton('Take Picture'),None,add_to = button_frame)
        picture_btn.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
        picture_btn.clicked.connect(self.take_picture)
        
        #Create Button
        create_btn = guts.widget_setup(qw.QPushButton('Create Pose / Clip'),None,add_to = frame)
        create_btn.setSizePolicy(qw.QSizePolicy.Expanding,qw.QSizePolicy.Expanding)
        create_btn.clicked.connect(self.create_pose_clip)
        
        back_btn = guts.widget_setup(self.back_button(),None,add_to = frame)
        
        self.widgets['pose'].clicked.connect(self.turn_off_timeline)
        self.widgets['clip'].clicked.connect(self.turn_off_timeline)
        
    def turn_off_timeline(self):
        if self.widgets['pose'].isChecked():
            self.timeline_area.setEnabled(False)
            self.timeline_btn.setEnabled(False)
        else:
            self.timeline_area.setEnabled(True)
            self.timeline_btn.setEnabled(True)
            
    def create_pose_clip(self):
        #Variables
        type = 'pose'
        name = self.pose_clip_name.text().replace(' ','_').lower()
        if self.widgets['clip'].isChecked() == True: type = 'clip'
        
        if name or name != '':
            rigs = list(set([guts.get_root_rig(x) for x in guts.rig_check()]))
            if rigs:
                characters = list(set([guts.get_root_rig(x).character_name.get() for x in guts.rig_check()]))
                day, time = guts.daytime()
                doc = ET.parse(XML_DOC)
                root = doc.getroot()
                prod = root.findall('Production')[INDEX]
                
                asset = ET.SubElement(prod,'Asset')
                char = ET.SubElement(asset,'Characters')
                for c in characters: ET.SubElement(char,c)
                asset.set('name',name)
                asset.set('type',type)
                asset.set('day',day)
                asset.set('time',time)
                asset.set('path','{0}{1}s/{2}/'.format(prod.get('path'),type,name))
                
                guts.publish_xml(root,XML_DOC)
                self.create_pose_clip_xml(name,type)
                self.get_poses_and_clips()
                self.change_index(0)
            
            else:
                message = "You need to select a character rig's anim to proceed."
                error = pm.confirmDialog(t = 'ERROR: Rig Not Selected',m = message,b = ['Okay'],cb = 'Okay')
    
    def get_key_range(self,anims,*args):
        range = []
        for anim in anims: range += pm.keyframe(anim,q=True)
        range = list(set(range))
        return [min(range),max(range)]
        
    def create_pose_clip_xml(self,name,kind):
        #Selected Items
        rigs = list(set([guts.get_root_rig(x) for x in guts.rig_check()]))
        original_selection = pm.ls(sl = True)
        
        #Folder Setup
        start = '{0}/{1}s'.format(LIBRARY,kind)
        path = '{0}/{1}'.format(start,name)
        doc = '{0}/{1}.xml'.format(path,kind)
        if not os.path.exists(start): os.mkdir(os.path.join(LIBRARY, '{0}s'.format(kind)))
        if not os.path.exists(path): os.mkdir(os.path.join(start, name))
        root = ET.Element(kind.title())
        
        for rig in rigs:
            char = mars.CharacterRig('','',node = rig)
            if self.widgets['all_anims'].isChecked() == True: anims = char.get_complete_rig_anims()
            else: anims = [x for x in original_selection if x.hasAttr('animNode') and x in char.get_complete_rig_anims()]
            
            xml_char = ET.SubElement(root,'Character')
            xml_char.set('rig',rig.character_name.get())
            xml_char.set('length',str(rig.length.get()))
            xml_char.set('width',str(rig.width.get()))
            xml_char.set('height',str(rig.height.get()))
            if kind == 'clip':
                min, max = self.get_key_range(anims)
                xml_char.set('min',str(min))
                xml_char.set('max',str(max))
                try:
                    if min < int(root.get('start')): root.set('start',str(min))
                except: root.set('start',str(min))
                try:
                    if max > int(root.get('end')): root.set('end',str(max))
                except: root.set('end',str(max))
            
            for anim in anims:
                if pm.keyframe(anim,q=True) or kind == 'pose':
                    node = guts.acquire_nodes(anim)[0]
                    attributes = anim.listAttr(w=True,u=True,v=True,k=True)
                    xml_anim = ET.SubElement(xml_char,'Anim')
                    xml_anim.set('name',anim.name().split(':')[-1])
                    xml_anim.set('side',node.side.get())
                    xml_anim.set('limb', node.limb.get())
                    xml_anim.set('component_name',node.name())
                    xml_anim.set('component_type',node.node_type.get())
                    
                    for at in attributes:
                        keys, key_values = self.get_anim_keys(at,kind)
                        
                        if keys or kind == 'pose':
                            xml_attr = ET.SubElement(xml_anim,'Attribute')
                            xml_attr.set('id',at.split('.')[-1])
                            
                            for i, key in enumerate(keys):
                                xml_key = ET.SubElement(xml_attr,'Key')
                                xml_key.set('frame',str(key))
                                xml_key.set('value',str(key_values[i]))
                                
                                if kind == 'clip':
                                    xml_key.set('ia',str(pm.keyTangent(at, time = (key), q = True, ia=True)[0]))
                                    xml_key.set('oa',str(pm.keyTangent(at, time = (key), q = True, oa = True)[0]))
                                    xml_key.set('iw',str(pm.keyTangent(at, time = (key), q = True, iw=True)[0]))
                                    xml_key.set('ow',str(pm.keyTangent(at, time = (key), q = True, ow=True)[0]))
                                    xml_key.set('itt',str(pm.keyTangent(at, time = (key), q = True, itt=True)[0]))
                                    xml_key.set('ott',str(pm.keyTangent(at, time = (key), q = True, ott = True)[0]))
                            
        if kind == 'pose': [x.set('frame','1.0') for x in root.findall('.//Key')]
        guts.publish_xml(root,doc)
        self.save_image(path)
        self.refresh_settings()
    
    def get_anim_keys(self,attribute,kind,type = 'clip',*args):
        if kind == 'pose':
            keys = [pm.currentTime()]
            key_values = [attribute.get()]
        else:
            keys = pm.keyframe(attribute,q=True)
            key_values = pm.keyframe(attribute,q=True, vc=True)
        
            if self.widgets[type + '_start_check'].isChecked():
                for key in keys:
                    if key < self.widgets[type + '_start'].value():
                        keys.remove(key)
                        key_values.remove(key_values[0])
            
            if self.widgets[type + '_end_check'].isChecked():
                for key in keys[::-1]:
                    if key > self.widgets[type + '_end'].value():
                        keys.remove(key)
                        key_values.remove(key_values[-1])
        
        return keys, key_values
    
    def refresh_settings(self):
        self.icon.setStyleSheet('')
        self.pose_clip_name.setText('')
        self.widgets['pose'].setChecked(True)
        self.widgets['all_anims'].setChecked(True)
        self.turn_off_timeline()
    
    def take_picture(self):
        temp_icon, temp_path = guts.viewport_image((250,250),(40,40))
        self.new_image = True
        self.icon.setStyleSheet('background-image: url(' + temp_path + ');' +
                                'background-repeat: no-repeat; background-position: center center;')
                                 
    def save_image(self,path):
        if self.new_image == True:
            temp_icon = pm.internalVar(userPrefDir=True) + '/temp_icon.png'
            temp_image = pm.internalVar(userPrefDir=True) + '/temp_image.png'
            shutil.move(temp_icon,path + '/.icon.png')
            shutil.move(temp_image,path + '/.image.png') 
#===============================================================================================================#
#PuppetMaster()