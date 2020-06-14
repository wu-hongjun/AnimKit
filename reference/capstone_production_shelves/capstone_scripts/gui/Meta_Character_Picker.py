import pymel.all as pm
import metaCore2 as m
import MARS as mars
import gui.GuiUtilities as guts
from functools import partial
import maya, os, shutil
import maya.OpenMayaUI as mui
import xml.etree.ElementTree as ET
import shiboken2 as shiboken
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg
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
    
GUI_LIBRARY = DESKTOP + "/capstone_scripts/character_gui/"
#===============================================================#    
#Correcting the color of the button.
def drag_button_color(btn,side,type,selected = False):
    c = ''
    if side == 'center': c = 'rgb(0,10,220)'
    elif side == 'left': c = 'rgb(0,180,220)'
    elif side == 'right': c = 'rgb(175,0,0)'

    if type == 'anim':
        clr = 'background-color: ' + c + ';'
        if selected == False: btn.setStyleSheet('QPushButton {' + clr + '}')
        else: btn.setStyleSheet('QPushButton {background-color: rgb(150,150,150); border-style: solid;'
                                'border-width: 1px; border-color: white;}'
                                'QPushButton:pressed {border-width: 2px;}')      
    if type in ['switch','function']:
        if selected == False:
            btn.setStyleSheet('QPushButton {background-color: rgb(120,120,120); border-style: solid;'
                              'border-width: 1px; border-color: ' + c + ';}'
                              'QPushButton:pressed {border-color: white; border-width: 2px;}')
        else:
            btn.setStyleSheet('QPushButton {background-color: rgb(150,150,150); border-style: solid;'
                              'border-width: 1px; border-color: white;}'
                              'QPushButton:pressed {border-width: 2px;}')    
    elif type == 'ui':
        if selected == False:
            btn.setStyleSheet('QPushButton {background-color: rgba(255,255,255,20); border: solid;'
                              'border-width: 1px; border-color: white;}'
                              'QPushButton:hover {background-color: rgba(255,255,255,60);}'
                              'QPushButton:pressed {background-color: rgba(255,255,255,90); border-width: 3px;}')
        else: btn.setStyleSheet('QPushButton {background-color: rgba(255,255,255,90); border: solid;'
                                'border-width: 3px; border-color: white;}')

#Fixes any numbering issues with the Buttons in the xml document
def xml_button_number_correction(document):
    correction = False
    doc = ET.parse(document)
    root = doc.getroot()
    for frame in root.findall('Frame'):
        buttons = frame.findall('Button')
        for i, btn in enumerate(buttons):
            num = int(btn.get('number'))
            if num != i:
                btn.set('number', str(i))
                correction = True
    if correction == True: save_xml_doc(document,root)

#Collects the UI Frames of the Picker GUI and sorts them according to the XML Document
def get_frames(ui,rig):
    gui = ui.gui_stack
    rig = rig.replace(' ','_')
    doc = ET.parse(GUI_LIBRARY + rig + '/.gui.xml')
    root = doc.getroot()
    frames = root.findall('Frame')
    ui_frames = []
    for frame in frames:
        for child in gui.children():
            try:
                if frame.get('name') == child.widget_name: ui_frames.append(child)
            except: pass
    return ui_frames
        
#Gets all the Rigs in a particular Scene and splits their reference name.
def get_rigs():     
    rigs = []
    ref_names = []
    start_names = []
    items = pm.ls('*_topCon', r=True)
    
    for item in items:
        if not pm.listConnections(item.connected_to)[0].hasAttr('connected_to'):
            for node in pm.listConnections(item.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Character_Rig': rigs.append(node)
                elif node.hasAttr('node_type') and node.node_type.get() == 'CharacterRig': rigs.append(node)
    
    for rig in rigs:
        if ':' in rig: ref_names.append(rig.name().replace(':' + rig.name().split(':')[-1],''))
        else: ref_names.append(rig.character_name.get().lower())
    
    return [rigs,ref_names]

#Makes the Folder and Document in the Library if neither exist.
def make_folder(rig):
    rig_name = rig.character_name.get()
    folders = ['images','functions']
    if not os.path.exists(GUI_LIBRARY + rig_name):
        os.mkdir(os.path.join(GUI_LIBRARY, rig_name))
        for folder in folders: os.mkdir(os.path.join((GUI_LIBRARY + rig_name + '/'), folder))
        if not os.path.exists(GUI_LIBRARY + rig_name + '/.gui.xml'): make_xml_doc(rig)

#Creates the default XML document.
def make_xml_doc(rig):
    rig_name = rig.character_name.get()
    location = GUI_LIBRARY + rig_name
    gui = ET.Element('GUI')
    main = ET.SubElement(gui,'Frame')
    main.set('name','main')
    root = ET.ElementTree(gui)
    indent(gui)
    root.write(location + '/.gui.xml')
 
#Script Found online to correct the odd spacing caused by parsing and re-saving an XML Document.   
def indent(elem, level=0):
    i = "\n" + (level*"\t")
    if len(elem):
        if not elem.text or not elem.text.strip(): elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip(): elem.tail = i
        for elem in elem: indent(elem, level+1)
        if not elem.tail or not elem.tail.strip(): elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()): elem.tail = i    
        
#Saving and reformatting the XML Document
def save_xml_doc(document,root):
    new = ET.ElementTree(root)
    indent(root)
    new.write(document)
    
def get_root_rig_from_obj(obj):
    rig = None
    if obj.hasAttr('connected_to'):
        component = pm.PyNode(get_node_from_obj(obj))
        if component.hasAttr('rig'): rig = pm.listConnections(component.rig)[0]
        elif component.hasAttr('character_name'): rig = pm.PyNode(component)
        if rig:
            while rig.hasAttr('connected_to'):
                rig = pm.PyNode(pm.listConnections(rig.connected_to)[0])
    return rig

def get_node_from_obj(obj):
    if obj.hasAttr('connected_to'):
        nodes = pm.listConnections(obj.connected_to)
        for node in nodes:
            if node.hasAttr('network_type') and node.network_type.get() != 'Multi_Constraint': return pm.PyNode(node)
            elif node.hasAttr('node_type') and node.node_type.get() != 'MultiConstraint': return pm.PyNode(node)
#===============================================================#
class DragButton(qw.QPushButton):
    lock = True
    selected = False
    def __init__(self,side,number,w,h,title,type,parent = None):
        super(DragButton,self).__init__(parent)
        
        self.side = side
        self.setText(title)
        self.setFixedSize(w,h)
        self.type = type
        self.w = w
        self.h = h
        self.number = number
            
        try: self.document = self.parent().document
        except: self.document = ''
        drag_button_color(self,self.side,self.type)
        
        self.show()
    
    #Corrects the stylesheet to the default mode        
    def correct_color(self):
        drag_button_color(self,self.side,self.type)
    
    #Updates the XML Document everytime the button is moved
    def write_to_xml(self):
        if self.document != '':
            parent_name = self.parent().widget_name
            doc = ET.parse(self.document)
            root = doc.getroot()
            btn = ''
            for frame in root.findall('Frame'):
                if frame.get('name') == parent_name:
                    buttons = frame.findall('Button')
                    if buttons:
                        for all in buttons:
                            if all.get('number') == str(self.number): btn = all
                    if btn == '': btn = ET.SubElement(frame,'Button')
                    btn.set('side',self.side)
                    btn.set('number',str(self.number))
                    btn.set('title',self.text())
                    btn.set('type',self.type)
                    btn.set('x',str(self.x()))
                    btn.set('y',str(self.y()))
                    btn.set('w',str(self.w))
                    btn.set('h',str(self.h))
                        
                    save_xml_doc(self.document,root)
    
    #If unlocked, allows the user to move the button around the ui space.
    def mousePressEvent(self, event):
        if self.lock == False:
            self.__mousePressPos = None
            self.__mouseMovePos = None
            if event.button() == qc.Qt.LeftButton:
                self.__mousePressPos = event.globalPos()
                self.__mouseMovePos = event.globalPos()
    
        else: super(DragButton, self).mousePressEvent(event)

    #If unlocked, allows the user to move the button around the ui space.
    def mouseMoveEvent(self, event):
        if self.lock == False:
            if event.buttons() == qc.Qt.LeftButton:
                # adjust offset from clicked point to origin of widget
                currPos = self.mapToGlobal(self.pos())
                globalPos = event.globalPos()
                diff = globalPos - self.__mouseMovePos
                newPos = self.mapFromGlobal(currPos + diff)
                self.move(newPos)
                self.correct_color()
                
                self.__mouseMovePos = globalPos
        else: super(DragButton, self).mouseMoveEvent(event)

    #Writes the new position down to the XML document.
    def mouseReleaseEvent(self, event):
        if self.lock == False:
            if self.__mousePressPos is not None:
                moved = event.globalPos() - self.__mousePressPos 
                self.write_to_xml()
                if moved.manhattanLength() > 3:
                    event.ignore()
                    return
                    
        else: super(DragButton, self).mouseReleaseEvent(event)
#===============================================================#
class ButtonFrame(qw.QFrame):
    widget_name = ''
    image_location = ''
    editable = False
    selected_buttons = []
    
    def __init__(self,name,ui,rig = None,ref_name = ''):
        super(ButtonFrame,self).__init__()
        self.buttons = {}
        self.name = name
        self.rig = rig
        self.ui = ui
        self.ref_name = ref_name + ':'
        
        self.setLayout(qw.QVBoxLayout())
        self.setFrameStyle(qw.QFrame.WinPanel | qw.QFrame.Plain)
        self.setFixedSize(430,530)
        self.rubberBand = qw.QRubberBand(qw.QRubberBand.Rectangle, self)
        self.origin = qc.QPoint()
        self.document = ''
        
        if rig != None:
            self.document = GUI_LIBRARY + rig.character_name.get() + '/.gui.xml'
            self.generate_button_layout()
            self.widget_name = self.name
            self.layout().setObjectName(name + 'UI')
            self.image_location = GUI_LIBRARY + rig.character_name.get() + '/images/' + name + '.png'
            self.setStyleSheet('QFrame {background-image: url(' + self.image_location + ');'
                               'background-color: rgb(30,30,30); background-repeat: no-repeat;'
                               'background-position: center center;}')
        
        else: self.setStyleSheet('QFrame{color: red; background-color: rgb(30,30,30);} QLabel{color: white;}')
    
    #Parents Drag Buttons to Frame based on XML Document and Frame
    def generate_button_layout(self):
        #Removes any buttons still there.
        for btn in self.children():
            if btn.__class__.__name__ == 'DragButton': btn.deleteLater()
            self.buttons = {}
        
        frames = ET.parse(self.document).getroot().findall('Frame')
        for all in frames:
            if all.get('name') == self.name: current_frame = all
        
        #Sets up 'anim', 'ui' or 'function' button functions.
        for btn in current_frame.findall('Button'):
            btn_name = self.name + '_btn_' + btn.get('number')
            side = btn.get('side')
            number = btn.get('number')
            w = int(btn.get('w'))
            h = int(btn.get('h'))
            title = btn.get('title')
            type = btn.get('type')
            self.buttons[btn_name] = DragButton(side, number, w, h, title, type, parent = self)
            self.buttons[btn_name].move(int(btn.get('x')),int(btn.get('y')))
            self.buttons[btn_name].lock = True
            self.buttons[btn_name].correct_color()
            
            if type == 'anim':
                selected_anim = self.ref_name + btn.find('Anim').get('name')
                self.buttons[btn_name].clicked.connect(partial(self.select_anim,selected_anim))
            elif type == 'ui':
                index = int(btn.find('UI').get('index'))
                self.buttons[btn_name].clicked.connect(partial(self.change_ui,index))
            elif type == 'function':
                num = int(btn.find('Function').get('number'))
                self.buttons[btn_name].clicked.connect(partial(self.run_function, num))
                
        #Sets up switch button functions
        for btn in current_frame.findall('Button'):
            if btn.get('type') == 'switch':
                anims = {'FK':[],'IK':[]}
                btn_name = self.name + '_btn_' + btn.get('number')
                number = btn.get('number')
                for s in anims:
                    items = [x.get('name') for x in btn.findall(s)]
                    for item in items:
                        b = current_frame.find("Button/Anim[@name='" + item + "']..")
                        try: anims[s].append(self.buttons[self.name + '_btn_' + b.get('number')])
                        except: pass

                btn_anim = self.ref_name + btn.find('Switch').get('name')
                switch_function = partial(self.switch_anim,btn_name,btn_anim,anims['FK'],anims['IK'])
                self.buttons[btn_name].clicked.connect(switch_function)
                self.switch_hide_buttons(btn_anim,anims['FK'],anims['IK'])
    
    def switch_hide_buttons(self,switch,FKs,IKs):
        switch = pm.PyNode(switch)
        if switch.FKIK_switch.get() == 0:
            for ik in IKs: ik.hide()
        else:
            for fk in FKs: fk.hide()
    
    def get_switch_items(self):
        ui = self.ui
        anims = {}
        items = []
        for s in ['FK','IK']:
            anims[s] = []
            for index in xrange(ui.widgets[s + '_switch_buttons'].count()):
                anims[s].append(ui.widgets[s + '_switch_buttons'].item(index))
                items.append(ui.widgets[s + '_switch_buttons'].item(index)) 
        return anims['FK'], anims['IK'], items
    
    #Generate new number for button
    def button_number(self,frame):
        numbers = []
        for all in frame.findall('Button'): numbers.append(int(all.get('number')))
        numbers = sorted(numbers)
        next_num = len(numbers)
        if numbers:
            if (len(numbers)-1) != int(numbers[-1]):
                i = 0
                for num in numbers:
                    if num != i:
                        next_num = i
                        break
                    i += 1
        return next_num
    
    def add_button(self):
        #Variables
        index = self.ui.ui_switch.currentIndex()
        
        ##XML Variables
        doc = ET.parse(self.document)
        root = doc.getroot()
        frames = root.findall('Frame')
        frame = frames[index]
        i = len(frame.findall('Button'))
        script_path = GUI_LIBRARY + self.rig.character_name.get() + '/functions/'
        script_num = str(len(os.listdir(script_path)))
        
        ##Button Settings
        ba = {'x':'0','y':'0'}
        ba['number'] = str(self.button_number(frame))
        ba['title'] = self.ui.button_text.text()
        ba['w'] = self.ui.widgets['width'].value()
        ba['h'] = self.ui.widgets['height'].value()
        ba['side'] = self.ui.widgets['side'].currentText().lower()
        ba['type'] = self.ui.widgets['type'].currentText().lower()
        btn_name = frame.get('name') + '_btn_' + ba['number']
        
        #Button Creation and Settings
        self.buttons[btn_name] = DragButton(ba['side'],ba['number'],ba['w'],ba['h'],ba['title'],ba['type'],parent = self)
        self.buttons[btn_name].lock = False
        self.buttons[btn_name].correct_color()
        self.buttons[btn_name].write_to_xml()
        
        btn = ET.SubElement(frame,'Button')
        for item in ba: btn.set(item,str(ba[item]))
        anim_name = self.ui.button_text.text()
        
        ##Button functionality
        if ba['type'] in ['anim','switch']:
            btn_f = ET.SubElement(btn,ba['type'].title())
            select_anim = self.ui.widgets[ba['type'] + '_button_text'].text()
            if select_anim != '': btn_f.set('name',select_anim)
            
            if ba['type'] == 'switch':
                anims = {}
                anims['FK'],anims['IK'],all_anims = self.get_switch_items()
                for s in ['FK','IK']:
                    for i in range(len(anims[s])):
                        sb = self.ui.widgets[s + '_switch_buttons'].item(i).text()
                        k = ET.SubElement(btn,s)
                        k.set('name',sb)
                            
        elif ba['type'] == 'ui':
            btn_f = ET.SubElement(btn,'UI')
            if self.ui.widgets['ui_selection'].currentIndex() != 0:
                btn_f.set('index',str(self.ui.widgets['ui_selection'].currentIndex()-1))
        else:
            string = self.ui.function_text.toPlainText()
            btn_f = ET.SubElement(btn,'Function')
            btn_f.set('number','')
            if string != '':
                func_doc = open(script_path + 'function_' + script_num + '.py','w').write(string)
                btn_f.set('number',script_num)
            
        #Saving newest version of the XML Document
        save_xml_doc(self.document,root)
    
    def delete_buttons(self):
        if len(self.selected_buttons) > 0:
            index = self.ui.ui_switch.currentIndex()
            
            ##XML Variables
            doc = ET.parse(self.document)
            root = doc.getroot()
            frames = root.findall('Frame')
            frame = frames[index]
            
            for btn in self.selected_buttons:
                b = self.buttons[btn]
                num = b.number
                frame.remove(frame.find("Button[@number='" + num + "']"))
                b.deleteLater()
                del self.buttons[btn]
            
            self.selected_buttons = []
            save_xml_doc(self.document,root)
    
    #Mirrors all the buttons in the variable self.selected_buttons
    def mirror_buttons(self):
        if len(self.selected_buttons) > 0:
            index = self.ui.ui_switch.currentIndex()
            
            ##XML Variables
            doc = ET.parse(self.document)
            root = doc.getroot()
            frames = root.findall('Frame')
            frame = frames[index]
            
            numbers = []
            for all in frame.findall('Button'): numbers.append(int(all.get('number')))
            start = sorted(numbers)[-1] + 1
            
            for j, btn in enumerate(self.selected_buttons):
                num = str(self.buttons[btn].number)
                b = frame.find("Button[@number='" + num + "']")
                
                type = b.get('type')
                title = b.get('title')
                side = b.get('side')
                x = int(b.get('x'))
                y = int(b.get('y'))
                w = int(b.get('w'))
                h = int(b.get('h'))
                
                if type == 'anim': element = b.find('Anim').get('name')
                elif type == 'switch': element = b.find('Switch').get('name')
                elif type == 'ui': element = b.find('UI').get('index')
                else: element = b.find('Function').get('number')
                
                center = (214 - int(w/2))
                i = start + j
                
                if side == 'left': side = 'right'
                elif side == 'right': side = 'left'
                try:
                    if 'left' in element: element = element.replace('left_','right_')
                    elif 'right' in  element: element = element.replace('right_','left_')
                except: pass
                
                if x > center: diff =  -(x - center) - (w/2)
                elif x < center: diff = (center - x) - (w/2)
                new_x = diff + 214
    
                btn_name = self.name + '_btn_' + str(i)
                self.buttons[btn_name] = DragButton(side,str(i),w,h,title,type,parent = self)
                self.buttons[btn_name].move(new_x,y)
                self.buttons[btn_name].lock = False
                self.buttons[btn_name].correct_color()
                self.buttons[btn_name].write_to_xml()
                
                #XML - Check to see if needed from here
                btn = ET.SubElement(frame,'Button')
                btn.set('side',side)
                btn.set('number',str(i))
                btn.set('title',title)
                btn.set('type',type)
                btn.set('x',str(new_x))
                btn.set('y',str(y))
                btn.set('w',str(w))
                btn.set('h',str(h))
                #To Here
                
                if type in ['anim','switch']:
                    btn_anim = ET.SubElement(btn,type.title())
                    btn_anim.set('name',element)
                    if type == 'switch':
                        for s in ['FK','IK']:
                            for anim in b.findall(s):
                                anim_name = anim.get('name')
                                if 'left' in anim_name: anim_name = anim_name.replace('left_','right_')
                                elif 'right' in anim_name: anim_name = anim_name.replace('right_','left_')
                                k = ET.SubElement(btn,s)
                                k.set('name',anim_name)
                        
                elif type == 'ui':
                    btn_anim = ET.SubElement(btn,'UI')
                    btn_anim.set('index',element)
                else:
                    btn_anim = ET.SubElement(btn,'Function')
                    btn_anim.set('number',element)
                            
            save_xml_doc(self.document,root)
                
            self.show_buttons_selection(selected = False)
            self.selected_buttons = []
    
    #Changes the Button Interface on the Character Picker UI, triggering the change.
    def change_ui(self,index):
        self.ui.ui_switch.setCurrentIndex(index)

    #Runs a custom script created by the UI designer.
    def run_function(self,num):
        if num != '':
            path = GUI_LIBRARY + self.rig.character_name.get() + '/functions/function_' + str(num) + '.py'
            string = open(path,'r')
            code = {}
            run_code = compile(string.read(),'<string>','exec')
            exec run_code in code
    
    #Assigned to a DragButton to select an anim
    def select_anim(self,anim):
        if anim != '':
            tgl = False
            modifiers = qw.QApplication.keyboardModifiers()
            if modifiers == qc.Qt.ShiftModifier: tgl = True
            pm.select(anim,tgl = tgl)

    #Assigned to DragButtons tied to an FKIK Switch
    def switch_anim(self,btn,anim,fks,iks):
        switch = pm.PyNode(anim)
        if switch.FKIK_switch.get(0) == 0:
            switch.FKIK_switch.set(1)
            for fk in fks: fk.hide()
            for ik in iks: ik.show()
        else:
            switch.FKIK_switch.set(0)
            for fk in fks: fk.show()
            for ik in iks: ik.hide()
    
    #Changes the editable variable which alters the mouse event functions and changes the frame border red.
    def edit_mode(self):
        if self.editable == True:
            self.editable = False
            self.setStyleSheet('QFrame {background-image: url(' + self.image_location + ');'
                               'background-color: rgb(30,30,30,); background-repeat: no-repeat;'
                               'background-position: center center;}')
            xml_button_number_correction(self.document)
            self.generate_button_layout()
        else:
            self.editable = True
            self.setStyleSheet('QFrame {background-image: url(' + self.image_location + ');'
                               'background-color: rgb(30,30,30); background-repeat: no-repeat;'
                               'color: red; background-position: center center;}')
                               
        self.button_edit_mode(self.editable)

    def button_edit_mode(self,editable):
        for btn in self.buttons:
            b = self.buttons[btn]
            if editable == True:
                b.lock = False
                b.show()
            else: b.lock = True
            drag_button_color(b,b.side,b.type)

    #Starts the process of creating a Marquee selection
    def mousePressEvent(self, event):
        if self.rig:
            if event.button() == qc.Qt.LeftButton:
                self.origin = qc.QPoint(event.pos())
                self.rubberBand.setGeometry(qc.QRect(self.origin, qc.QSize()))
                self.rubberBand.show()
            elif event.button() == qc.Qt.RightButton:
                par = mui.MQtUtil.fullName(long(shiboken.getCppPointer(self.layout())[0]))
                from gui.Meta_Marking_Menu import MetaMarkingMenu
                pop = MetaMarkingMenu(parent = par)
            
        else: super(ButtonFrame,self).mousePressEvent(event)
    
    #Allows the Marquee select to create with the movement of the mouse
    def mouseMoveEvent(self, event):
        if self.rig:
            if not self.origin.isNull():
                self.rubberBand.setGeometry(qc.QRect(self.origin, event.pos()).normalized())
        else: super(ButtonFrame,self).mouseMoveEvent(event)
    
    #Any Drag Button tied to an anim will be selected and the Marquee will hide.
    def mouseReleaseEvent(self, event):
        if self.rig:
            #XML Variables
            self.document = GUI_LIBRARY + self.rig.character_name.get() + '/.gui.xml'
            root = ET.parse(self.document).getroot()
            frames = root.findall('Frame')
            for all in frames:
                if all.get('name') == self.name: frame = all
                
            #Mouse Modifiers    
            if event.button() == qc.Qt.LeftButton:
                shift = False
                ctrl = False
                if event.modifiers() & qc.Qt.ShiftModifier: shift = True
                if event.modifiers() & qc.Qt.ControlModifier: ctrl  = True
                
                if ctrl == False and shift == False:
                    pm.select(cl = True)
                    self.selected_buttons = []
                    
                rubberband_rect = qc.QRect(self.rubberBand.geometry())
                
                if self.editable == True:
                    for all in self.buttons:
                        self.buttons[all].selected = False
                        self.buttons[all].correct_color()
                
                for all in self.buttons:
                    btn_name = all
                    btn = self.buttons[btn_name]
                    btn_geo = btn.geometry().normalized()
                    if rubberband_rect.intersects(btn_geo) == True and btn.isVisible():
                        num = int(btn.number)
                        x = frame.find("Button[@number='" + str(num) + "'][@type='anim']")
                        if x != None and self.editable == False:
                            anim = self.ref_name + x.find('Anim').get('name')
                            if anim != None:
                                if ctrl == True and shift == False: pm.select(anim,d = True)
                                elif ctrl == True and shift == True: pm.select(anim,add = True)
                                else: pm.select(anim,tgl = True)
                        else: self.selected_buttons.append(btn_name)
                                
                if self.editable == True: self.show_buttons_selection()
                self.rubberBand.hide()
                
        else: super(ButtonFrame,self).mouseReleaseEvent(event)

    def show_buttons_selection(self,selected = True):
        for all in self.selected_buttons:  
            btn = self.buttons[all]
            btn.selected = selected
            drag_button_color(btn,btn.side,btn.type,selected = selected)
        
#============================================================================================================================#
'''Method by Justin Israel'''

class AttrChannel(qw.QTableWidgetItem):
    def __init__(self):
        super(AttrChannel,self).__init__()
        
        self.attr_name = ''
        self.attr_value = None

        if self.attr_value is not None: self.set_attr_val(self.attr_value)
        
    def set_attr_value(self,val):
        if self.attr_value is not None:
            
            t = type(self.attr_value)
            try: val = t(val)
            except ValueError: val = self.attr_value
            else: self.attr_value = val
            
            if isinstance(val, float):
                f_val = str(round(val,3))
                if f_val.endswith('.0'): f_val = f_val.split('.')[0]
                self.setText(f_val)
                
            elif isinstance(val, bool):
                if val == True: self.setText('on')
                elif val == False: self.setText('off')
            else: self.setText(str(val))

#============================================================================================================================#
class EnumChannel(qw.QComboBox):
    def __init__(self,attr_name):
        super(EnumChannel,self).__init__()
        
        self.attr_name = attr_name
        obj, attr = attr_name.split('.')
        
        enum_items = [str(x) for x in pm.attributeQuery(attr,n = obj,le = True)[0].split(':')]
        for item in enum_items: self.addItem(item)
        self.setStyleSheet ("QComboBox {background-color: rgb(70,70,70);}"
                            "QComboBox::drop-down {border: 0px;}"
                            "QComboBox::down-arrow {image: url(noimg);}")
        self.setCurrentIndex(pm.Attribute(obj + '.' + attr).get())
        
        self.currentIndexChanged.connect(self.enum_change)
        
    def enum_change(self):
        index = self.currentIndex()
        pm.setAttr(self.attr_name,index)
        
#============================================================================================================================#
class ChannelBox(qw.QFrame):
    widgets = {}
    def __init__(self,parent = None):
        super(ChannelBox,self).__init__(parent)
        self.setStyleSheet('QFrame{background-color: rgb(70,70,70); color: rgb(180,180,180);}')
        
        guts.widget_setup(self,qw.QVBoxLayout(),cm = (5,0,5,5))
        self.setFrameStyle(qw.QFrame.StyledPanel)
        
        #Obj Label
        self.obj_label = guts.widget_setup(qw.QLabel(''),None,add_to = self)
        self.obj_label.setFixedHeight(20)
        obj_font = qg.QFont()
        obj_font.setPointSize(9)
        obj_font.setBold(True)
        self.obj_label.setFont(obj_font)
        
        #Table
        self.table = guts.widget_setup(qw.QTableWidget(1,3),None,add_to = self)
        self.table.setSpan(0,0,1,2)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0,qw.QHeaderView.Stretch)
        self.table.setColumnWidth(1,10)
        self.table.setColumnWidth(2,75)
        self.table.setStyleSheet('QTableWidget {border: none;}')
        
        edit_triggers = self.table.DoubleClicked|self.table.SelectedClicked|self.table.AnyKeyPressed
        self.table.setEditTriggers(edit_triggers)
        
        self.table.setItemPrototype(AttrChannel())
        self.table.installEventFilter(self)

        self.change_channel_box()
        
        self.table.itemChanged.connect(self.value_change)
        self.table.itemSelectionChanged.connect(self.drag_value_change)
        
        self.setContextMenuPolicy(qc.Qt.ActionsContextMenu)
        
        for all in ['key_selected','key_all_attributes','delete_keys','delete_all_attribute_keys','return_to_default']:
            self.widgets[all] = qw.QAction(self)
            self.widgets[all].setText(all.replace('_',' ').title())
            self.addAction(self.widgets[all])
       
        self.widgets['key_selected'].triggered.connect(partial(self.key_attribute,'selected'))
        self.widgets['key_all_attributes'].triggered.connect(partial(self.key_attribute,'all'))
        self.widgets['delete_keys'].triggered.connect(partial(self.delete_keys,'selected'))
        self.widgets['delete_all_attribute_keys'].triggered.connect(partial(self.delete_keys,'all'))
        self.widgets['return_to_default'].triggered.connect(self.default_value)
        
        #Activates Timer to change the channel box 
        self.attr_channels = []
        self.attr_items = []
        self.refresh_timer()

    def delete_keys(self,type):
        selection = pm.ls(sl = True)
        for obj in selection:
            if type == 'selected':
                for item in self.table.selectedItems():
                    at = item.attr_name.split('.')[-1]
                    try: pm.cutKey(obj,at = at)
                    except: pass
            else:
                attrs = pm.listAttr(obj,r=True, w=True, v=True, k=True)
                for at in attrs: pm.cutKey(obj,at = at)
    
    def key_attribute(self,type):
        selection = pm.ls(sl = True)
        for obj in selection:
            if type == 'selected':
                for item in self.table.selectedItems():
                    at = item.attr_name.split('.')[-1]
                    try: pm.setKeyframe(obj + '.' + at, t = pm.currentTime())
                    except: print obj + '.' + at
            else:
                attrs = [obj + '.' + x for x in pm.listAttr(obj,r=True, w=True, v=True, k=True)]
                for at in attrs: pm.setKeyframe(at, t = pm.currentTime())
            
    def default_value(self):
        selection = pm.ls(sl = True)
        for obj in selection:
            for item in self.table.selectedItems():
                at = item.attr_name.split('.')[-1]
                dv = pm.attributeQuery(at,n=obj,ld=True)[0]
                obj.attr(at).set(dv)
                
    
    #Creates a timer that checks if attribute changes and adjusts the channel box accordingly.
    def refresh_timer(self):
        self.refresher = qc.QTimer()
        self.refresher.setInterval(100)
        self.refresher.timeout.connect(self.attributes_from_obj)
        self.refresher.start()
    
    #Refreshes the channel box when the selection is changed.
    def change_channel_box(self):
        self.attr_channels = []
        self.attr_items = []
        while self.table.rowCount() > 0: self.table.removeRow(0)
        obj_name = ''
        self.obj_label.setText(obj_name)
        selection = pm.ls(sl = True)
        if len(selection) > 0:
            obj = selection[-1] 
            obj_name = obj.name()
            if len(obj_name) > 38: obj_name = obj_name[0:38] + '...'
            self.obj_label.setText(obj_name)
            attrs = pm.listAttr(obj,r=True, w=True, v=True, k=True)
            
            self.table.setRowCount(len(attrs))
            for row, attr in enumerate(attrs):
                #row += 1
                self.table.setRowHeight(row,20)
                full_attr = obj.name() + '.' + attr
                
                name = pm.attributeName(full_attr) + '  '
                attribute_type = pm.attributeQuery(attr,n = obj.name(),at = True)
                
                item = qw.QTableWidgetItem(name)
                item.attr_name = full_attr
                item.setFlags(item.flags() ^ qc.Qt.ItemIsEditable)
                item.setTextAlignment(qc.Qt.AlignRight|qc.Qt.AlignVCenter)
                self.table.setItem(row,0,item)
                self.attr_items.append(item)
                
                key_item = qw.QTableWidgetItem('')
                key_item.setFlags(qc.Qt.NoItemFlags)
                self.table.setItem(row,1,key_item)
                if self.key_check(full_attr) == True:
                    key_item.setBackgroundColor(qg.QColor(200,0,0))

                self.table.blockSignals(True)
                if attribute_type != 'enum':
                    val = pm.getAttr(full_attr)
                    slider = AttrChannel()
                    slider.setTextAlignment(qc.Qt.AlignLeft|qc.Qt.AlignVCenter)
                    slider.setBackgroundColor(qg.QColor(40,40,40))
                    slider.attr_name = full_attr
                    slider.attr_value = val 
                    slider.set_attr_value(val)
                    self.table.setItem(row, 2, slider)
                    self.attr_channels.append(slider)
                    
                else:
                    enum = EnumChannel(full_attr)
                    self.table.setCellWidget(row,2,enum)
                    self.attr_channels.append(enum)
                
                self.table.blockSignals(False)
    
    #Checks if attribute has keys on it.
    def key_check(self,attribute):
        keyed = False
        keys = []
        keys += pm.keyframe(attribute,q=True)
        if len(keys) > 0: keyed = True
        return keyed   
    
    #Changes Channel Box according to what's happening in the real scene.
    def attributes_from_obj(self):
        selection = pm.ls(sl = True)
        table = self.table
        if len(selection) > 0:
            self.table.blockSignals(True)
            for channel in self.attr_channels:
                if channel.__class__.__name__ == 'AttrChannel':
                    channel.set_attr_value(pm.Attribute(channel.attr_name).get())
                else: channel.setCurrentIndex(pm.Attribute(channel.attr_name).get())
            for item in self.attr_items:
                key_item = self.table.item(item.row(),1)
                if self.key_check(item.attr_name) == True:
                    key_item.setBackgroundColor(qg.QColor(200,0,0))
                else: key_item.setBackgroundColor(qg.QColor(70,70,70))
            self.table.blockSignals(False)
         
    def drag_value_change(self):
        if pm.dragAttrContext( 'channel_box_drag', ex = True) == True: pm.deleteUI('channel_box_drag')
        attrs = []
        ct = []
        for item in self.table.selectedItems():
            if item.column() == 0: attrs.append(item.attr_name.split('.')[-1])
        objs = pm.ls(sl = True)
        for obj in objs:
            for attr in attrs:
                if obj.hasAttr(attr) and pm.getAttr(obj.name() + '.' + attr,l = True) == False:
                    ct.append(str(obj.name() + '.' + attr))           
        d = pm.dragAttrContext('channel_box_drag', ct = ct)
        pm.setToolTo(d)
    
    #Makes sure that the attribute used not exceeding the min or max values.
    def correct_attribute(self,attribute,value):
        if isinstance(value,float):
            node, at = attribute.split('.')
            try: min = pm.attributeQuery(at, n = node,min = True)[0]
            except: min = None
            try: max = pm.attributeQuery(at, n = node,max = True)[0]
            except: max = None
            if min != None and value < min: value = min
            elif max != None and value > max: value = max
        return value
            
    #Applies values typed into the channel box to selected attributes.
    def value_change(self, item):
        row = item.row()
        column = item.column()
        
        if column == 2:
            txt = str(item.text())
            full_attr =  item.attr_name
            obj, attr = full_attr.split('.')
            at_type = type(item.attr_value)
            
            if at_type is bool: attr_value = txt.lower() in ('1','on','yes','y','true')
            else: attr_value = at_type(txt)
            
            self.table.blockSignals(True)
            for obj in pm.ls(sl = True):
                try:
                    n, attr = full_attr.split('.')
                    c_val = self.correct_attribute((obj + '.' + attr),attr_value)
                    pm.setAttr((obj + '.' + attr),c_val)
                    item.set_attr_value(c_val)  
                except: pass
            self.table.blockSignals(False)
            
            for obj in pm.ls(sl = True):
                for i in self.table.selectedItems():
                    if i.column() != 2: continue
                    if i is item: continue
                    try:
                        n, attr = i.attr_name.split('.')
                        c_val = self.correct_attribute((obj + '.' + attr),attr_value)
                        i.set_attr_value(c_val)
                        pm.setAttr((obj + '.' + attr),c_val)
                    except: pass
                    
    def eventFilter(self,obj,event):
        if obj is self.table:
            if event.type() == event.KeyPress:
                self.table.keyPressEvent(event)
                event.accept()
                return True
        return False
#============================================================================================================================#
class MetaCharacterPicker(qw.QWidget):
    widgets = {}
    selected_anims = []
    def __init__(self,parent = guts.get_main_window()):
        super(MetaCharacterPicker,self).__init__(parent)
        
        ##Checks if PySide window Exists##
        if pm.window('MetaCharacterPicker',ex=True) == True: pm.deleteUI('MetaCharacterPicker',wnd=True)
        
        #Gets the list of all rigs and references in the scene
        self.rigs, self.ref_names = get_rigs()
        
        #Window Setup
        self.setObjectName('MetaCharacterPicker')
        self.setWindowTitle('Meta Character Picker')
        self.setWindowFlags(qc.Qt.Tool)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        guts.widget_setup(self,qw.QHBoxLayout(),cm = (5,5,5,5),spacing = 5)
        self.setFixedSize(700,605)
        
        #Gets the list of all rigs and references in the scene
        self.character_area = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,cm = (0,0,0,0),add_to = self)
        self.character_area.setFixedWidth(430)
        
        #Character Settings
        self.character_settings = guts.widget_setup(qw.QFrame(),qw.QHBoxLayout(),cm = (0,5,0,5),add_to = self.character_area)
        self.character_settings.setFixedHeight(30)
        
        ####Rig Switch
        char_label = guts.widget_setup(qw.QLabel('Character: '),None,add_to = self.character_settings)
        char_label.setFixedWidth(55)
        
        self.rig_switch = guts.center_combobox(items = [x.title() for x in self.ref_names],widget = self.character_settings)
        self.rig_switch.setFixedHeight(25)
        
        ##GUI Stack
        self.gui_stack = guts.widget_setup(qw.QStackedWidget(),None,add_to = self.character_area)
        self.gui_stack.setFixedSize(430,530)
        
        #Lower Widget
        self.lower_widget = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = 5,add_to = self.character_area)
        
        #UI Stack
        self.ui_stack = guts.widget_setup(qw.QStackedWidget(),None,add_to = self.lower_widget)
        
        ##UI Settings
        self.ui_settings = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = None)
        self.ui_stack.addWidget(self.ui_settings)
        
        ####UI Switch
        ui_label = guts.center_label('Frame: ',widget = self.ui_settings)
        ui_label.setFixedWidth(35)
        
        self.ui_switch = guts.center_combobox(widget = self.ui_settings)
        self.ui_switch.setFixedHeight(25)
        
        #Functions
        self.functions = guts.widget_setup(qw.QStackedWidget(),None,add_to = self)
        self.functions.setFixedWidth(250)

        #Default Functions
        self.default_functions = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5)
        self.functions.addWidget(self.default_functions)
        
        ##Channel Box
        self.channel_box = guts.widget_setup(ChannelBox(),None,add_to = self.default_functions)
        
        ##Default Buttons
        self.default_buttons = guts.widget_setup(qw.QFrame(),qw.QGridLayout(),spacing = None,cm = (5,5,5,5),add_to = self.default_functions)
        self.default_buttons.setFrameStyle(qw.QFrame.StyledPanel)
        self.default_buttons.setFixedHeight(95)
        
        j = 0
        for i, btn in enumerate(['default_pose','select_all_anims','key_selected','key_all_anims']):
            if i > 1:
                i -= 2
                j = 1
            self.widgets[btn] = guts.widget_setup(qw.QPushButton(btn.replace('_',' ').title()),None,add_to = [self.default_buttons,j,i])
            self.widgets[btn].setFixedHeight(35)
            
        ##Edit Functions
        '''if os.getenv("USERNAME") in gp.ADMINS:
            ####Edit Button
            self.edit_gui_btn = guts.widget_setup(qw.QPushButton('Edit GUI'),None,add_to = self.lower_widget)
            self.edit_gui_btn.setFixedSize(75,25)
            self.edit_gui_btn.clicked.connect(partial(self.edit_gui,self.rigs))
            
            self.edit_ui_tools()
            self.edit_button_tools()
            
            self.edit_layout_btns = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = None,add_to = self.ui_stack)
            
            for i, btn in enumerate(['edit_ui','edit_buttons']):
                self.widgets[btn] = qw.QPushButton(btn.replace('_',' ').title().replace('Ui','UI'))
                self.widgets[btn].setFixedHeight(25)
                self.edit_layout_btns.layout().addWidget(self.widgets[btn])
                self.widgets[btn].clicked.connect(partial(self.edit_function_switch,(i + 1)))'''
                
        #Functions
        self.ui_switch.currentIndexChanged.connect(self.switch_ui)
        self.rig_switch.currentIndexChanged.connect(partial(self.change_rig,self.rigs))
        self.widgets['key_selected'].clicked.connect(self.key_selected)
        self.widgets['key_all_anims'].clicked.connect(self.key_all_anims)
        self.widgets['select_all_anims'].clicked.connect(self.select_all_anims)
        self.widgets['default_pose'].clicked.connect(self.default_pose)
        
        #Load UI Elements
        self.change_rig(self.rigs)
        self.editable = False
        self.show()
        
        #ScriptJobs
        self.widgets['selection_change'] = pm.scriptJob( e= ["SelectionChanged",self.selection_change])
    #=============================================================================================#
    #Default Functions
    #=============================================================================================#
    #Adds the UI Frames from the XML document to the ui_switch
    def load_ui_frames(self,rig):
        self.ui_switch.blockSignals(True)
        
        for i in range(0,self.ui_switch.count()): self.ui_switch.removeItem(i)
        rig_name = rig.character_name.get()
        doc = GUI_LIBRARY + rig_name + '/.gui.xml'
        
        if os.path.exists(doc):
            frames = ET.parse(doc).getroot().findall('Frame')
            try: 
                for i in range(len(frames)): self.ui_switch.removeItem(i)
            except: pass
            for frame in frames:
                self.ui_switch.addItem(frame.get('name').replace('_',' ').title())
        else: self.ui_switch.addItem('Main')

        self.ui_switch.blockSignals(False)
        
    #Changes the Button Interface on the Character Picker UI, triggering the change.
    def edit_function_switch(self,index):
        self.functions.setCurrentIndex(index)
        
    def switch_ui(self):
        self.selection_change()
        index = self.ui_switch.currentIndex()
        self.gui_stack.setCurrentIndex(index)

    #Gets the default values of all attributes of currently selected anim and resets them.
    def default_pose(self):
        for anim in pm.ls(sl = True):
            attrs = anim.listAttr(w=True,u=True,v=True,k=True)
            for attr in attrs:
                a = attr.replace((anim + '.'),'')
                dv = pm.attributeQuery(a,n=anim,ld=True)[0]
                anim.attr(a).set(dv)
    
    #Keys all anims currently selected using the variable self.selected_anims
    def key_selected(self):
        for anim in pm.ls(sl = True): pm.setKeyframe(anim, hi = 'None', shape = False)
        self.channel_box.attributes_from_obj()
        
    #Selects all current rig anims
    def select_all_anims(self):
        rig = self.rigs[self.rig_switch.currentIndex()]
        if rig.hasAttr('network_type') and rig.network_type.get() == 'Character_Rig': char = m.Character_Rig('',pm.listConnections(rig.root)[0])
        elif rig.hasAttr('node_type') and rig.node_type.get() == 'CharacterRig': char = mars.CharacterRig('','',node = rig)
        char.select_complete_rig_anims()
    
    def key_all_anims(self):
        original_selection = pm.ls(sl = True)
        pm.select(cl = True)
        self.select_all_anims()
        self.key_selected()
        pm.select(original_selection)
        
    #Deletes old setup and creates the Button Frame setup for the currently selected rig.
    def change_rig(self,rigs,*args):
        for f in self.gui_stack.children():
            if f.__class__.__name__ == 'ButtonFrame': f.deleteLater()
            
        if rigs:
            self.load_ui_frames(rigs[self.rig_switch.currentIndex()])
            rig = rigs[self.rig_switch.currentIndex()]
            rig_name = rig.character_name.get()
            
            #Ref Name
            ref_name = ''
            if ':' in rig: ref_name = rig.name().replace(':' + rig.name().split(':')[-1],'')
            
            folder = GUI_LIBRARY + rig_name
            document = folder + '/.gui.xml'
            make_folder(rig)
            
            ##Button Layout
            doc = ET.parse(document)
            frames = doc.findall('Frame')
            for frame in frames:
                name = frame.get('name')
                self.widgets[name + '_ui'] = ButtonFrame(name,self,rig = rig,ref_name = ref_name)
                self.gui_stack.addWidget(self.widgets[name + '_ui'])
            self.selection_change()
            
        else:
            temp = ButtonFrame('temp',None)
            message = ('WARNING:\n\nThere are no MetaCore or MARS rigs detected.\n\n'
                       'Please open a file containing MetaCore or MARS components.\n\n')
            temp_message = guts.center_label(message,widget = temp)
            self.gui_stack.addWidget(temp)
            
    #Activates the editablility of the frames in the GUI
    def edit_gui(self,rigs):
        rig = rigs[self.rig_switch.currentIndex()]
        rig_name = rig.character_name.get()
        widgets = get_frames(self,rig_name)
        self.default_button_settings()
        if self.functions.currentIndex() == 0:
            editable = True
            self.functions.setCurrentIndex(1)
            self.ui_stack.setCurrentIndex(1)
            self.edit_gui_btn.setStyleSheet('border-style: solid; border-width: 2px; border-color: red;')
        else:
            editable = False
            self.ui_stack.setCurrentIndex(0)
            self.functions.setCurrentIndex(0)
            self.edit_gui_btn.setStyleSheet('')
        
        for widget in widgets: widget.edit_mode()
    
    #==========================================================================================================================#
    #Edit Tools and Functions
    #==========================================================================================================================#
    def edit_ui_tools(self):
        self.new_image = False
        if self.rig_switch.currentText() != '':
            rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
            document = GUI_LIBRARY + rig + '/.gui.xml'
            
            self.edit_ui_tools = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 5,add_to = self.functions)
            
            ##Image Tools
            self.ui_image_tools = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),spacing = None,cm = None,add_to = self.edit_ui_tools)
            self.ui_image_tools.setFrameStyle(qw.QFrame.StyledPanel)
    
            self.ui_image = guts.widget_setup(qw.QFrame(),None,add_to = self.ui_image_tools)
            self.ui_image.setFixedSize(215,265)
            self.ui_image.setFrameStyle(qw.QFrame.WinPanel | qw.QFrame.Plain)
            self.ui_image_tools.layout().setAlignment(qc.Qt.AlignCenter)
            
            ####Image Buttons
            self.image_buttons = qw.QGridLayout()
            self.image_buttons.setContentsMargins(0,0,0,0)
            self.ui_image_tools.layout().addLayout(self.image_buttons)
            for i, btn in enumerate(['take_picture','save_image']):
                self.widgets[btn] = guts.widget_setup(qw.QPushButton(btn.replace('_',' ').title()),None,add_to = [self.image_buttons,0,i])
                self.widgets[btn].setFixedHeight(30)
            
            #Widgets
            self.ui_tools = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),cm = None,spacing = None,add_to = self.edit_ui_tools)
            self.ui_tools.setFrameStyle(qw.QFrame.StyledPanel)
            
            ##UI Tools
            self.ui_list = guts.widget_setup(qw.QListWidget(),None,add_to = self.ui_tools)
            try: self.get_xml_frames(document)
            except: self.ui_list.addItem('main')
                
            self.ui_list.setCurrentRow(0)
            self.ui_name_area = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = None,add_to = self.ui_tools)
            
            frame_label = guts.widget_setup(qw.QLabel('Name: '),None,add_to = self.ui_name_area)
            self.new_frame_name = guts.widget_setup(qw.QLineEdit(),None,add_to = self.ui_name_area)
            
            self.ui_button_area = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout(),spacing = 5,add_to = self.ui_tools)
            
            for btn in ['add_ui','rename_ui','delete_ui']:
                self.widgets[btn] = guts.widget_setup(qw.QPushButton(btn.replace('_',' ').title().replace('Ui','UI')),None,add_to = self.ui_button_area)
                self.widgets[btn].setFixedHeight(30)
                
            #Functions
            self.widgets['add_ui'].clicked.connect(self.add_ui)
            self.widgets['rename_ui'].clicked.connect(self.rename_ui)
            self.widgets['delete_ui'].clicked.connect(self.delete_ui)
            self.widgets['take_picture'].clicked.connect(self.take_picture)
            self.widgets['save_image'].clicked.connect(self.save_image)
            self.ui_list.currentRowChanged.connect(self.ui_list_switch)
    
    def get_xml_frames(self,document):
        doc = ET.parse(document)
        root = doc.getroot()
        frames = root.findall('Frame')
        for frame in frames: self.ui_list.addItem(frame.get('name'))
        self.ui_list.item(0).setSelected(True)
        
    def take_picture(self):
        globals = pm.PyNode('defaultRenderGlobals')
        globals.imageFormat.set(32)
        p = pm.getPanel( type='modelPanel' )[-1]
        nc = pm.modelEditor(p, q = True, nurbsCurves = True)
        ns = pm.modelEditor(p, q = True, nurbsSurfaces = True)
        pm.modelEditor(p, e = True, nurbsCurves = False, nurbsSurfaces = False)
        
        temp_path = pm.internalVar(userPrefDir=True) + '/temp_image.png'
        asset_image = pm.playblast(frame=[1], fmt = 'image',v = False, cf = temp_path,wh=(215,265), orn = False, p = 100)
        
        self.new_image = True
        self.ui_image.setStyleSheet('background-image: url(' + asset_image + ');' +
                                    'background-repeat: no-repeat; background-position: center center;')
        
        self.ui_image.setStyleSheet('background-image: url(' + asset_image + '); background-repeat: no-repeat; background-position: center center;')
        pm.modelEditor(p, e = True, nurbsCurves = nc, nurbsSurfaces = ns)
        
    def ui_list_switch(self):
        self.ui_switch.setCurrentIndex(self.ui_list.currentRow())
                                            
    def save_image(self):
        if self.new_image == True:
            rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
            image_name = self.ui_list.currentItem().text()
            image_path = GUI_LIBRARY + rig + '/images/' + image_name + '.png'
            
            p = pm.getPanel( type='modelPanel' )[-1]
            nc = pm.modelEditor(p, q = True, nurbsCurves = True)
            ns = pm.modelEditor(p, q = True, nurbsSurfaces = True)
            pm.modelEditor(p, e = True, nurbsCurves = False, nurbsSurfaces = False)
            
            asset_image = pm.playblast(frame=[1], fmt = 'image',v = False, cf = image_path, wh=(430,530), orn = False, p = 100)
            self.widgets[image_name + '_ui'].setStyleSheet('QFrame{background-image: url(' + asset_image + '); color: red;'
                                                           'background-color: rgb(30,30,30); background-repeat: no-repeat;'
                                                           'background-position: center center;}')
            
            pm.modelEditor(p, e = True, nurbsCurves = nc, nurbsSurfaces = ns)

    def add_ui(self):
        if self.new_frame_name.text() != '':
            rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
            document = GUI_LIBRARY + rig + '/.gui.xml'
            char = self.rigs[self.rig_switch.currentIndex()]
            
            name = self.new_frame_name.text().replace(' ','_').lower()
            doc = ET.parse(document)
            root = doc.getroot()
            frame = ET.SubElement(root,'Frame')
            frame.set('name',name)
            save_xml_doc(document,root)
            
            self.ui_list.addItem(name)
            self.widgets[name + '_ui'] = ButtonFrame(name,self,rig = char)
            self.widgets[name + '_ui'].edit_mode()
            self.gui_stack.addWidget(self.widgets[name + '_ui'])

            num = self.ui_list.count() - 1
            self.ui_list.setCurrentRow(num)
            self.gui_stack.setCurrentIndex(self.ui_list.count() - 1)
            
            self.ui_switch.addItem(name.replace('_',' ').title())
            self.ui_switch.setCurrentIndex(self.ui_list.count() - 1)
    
    def rename_ui(self):
        if self.new_frame_name.text() != '':
           new_name = self.new_frame_name.text().replace(' ','_').lower()
           rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
           document = GUI_LIBRARY + rig + '/.gui.xml'
           char = self.rigs[self.rig_switch.currentIndex()]
           current_name = self.ui_list.currentItem().text()
           doc = ET.parse(document)
           root = doc.getroot()
           frame = root.find(".//Frame[@name='" + current_name + "']")
           frame.set('name',new_name)
           os.rename(GUI_LIBRARY + rig + '/images/' + current_name + '.png',GUI_LIBRARY + rig + '/images/' + new_name + '.png')
           save_xml_doc(document,root)
           self.ui_list.currentItem().setText(new_name)

    def delete_ui(self):
        rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
        document = GUI_LIBRARY + rig + '/.gui.xml'
        char = self.rigs[self.rig_switch.currentIndex()]
            
        doc = ET.parse(document)
        root = doc.getroot()
        name = self.ui_list.currentItem().text()
        xml_frame = root.find(".//Frame[@name='" + name + "']")
        root.remove(xml_frame)
        save_xml_doc(document,root)
        
        name = self.ui_list.currentItem().text()
        num = self.ui_list.currentRow()
        self.widgets[name + '_ui'].deleteLater()
        self.ui_list.takeItem(num)
        self.ui_switch.removeItem(num)
        
    #==========================================================================================================================#
    #Edit Button Tools and Functions
    #==========================================================================================================================#
    def edit_button_tools(self):
        if self.rig_switch.currentText() != '':
            rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
            document = GUI_LIBRARY + rig + '/.gui.xml'
            
            self.add_button_tools = guts.widget_setup(qw.QFrame(),qw.QVBoxLayout(),spacing = 5)
            self.add_button_tools.setFrameStyle(qw.QFrame.StyledPanel)
            self.add_button_tools.layout().setAlignment(qc.Qt.AlignCenter)
            self.functions.addWidget(self.add_button_tools)
            
            #Button Preview
            self.button_preview = guts.widget_setup(qw.QFrame(),qw.QGridLayout(),cm = None,spacing = None,add_to = self.add_button_tools)
            self.button_preview.setFixedSize(247,247)
            self.button_preview.setFrameStyle(qw.QFrame.WinPanel | qw.QFrame.Plain)
            self.button_preview.setStyleSheet('QFrame {background-color: rgb(30,30,30);}')
            
            self.temp_button = guts.widget_setup(qw.QPushButton(),None,add_to = [self.button_preview,0,0])
            self.temp_button.setFixedSize(15,15)
            
            #Parameter Settings
            self.parameters = guts.widget_setup(qw.QWidget(),qw.QFormLayout(),spacing = None,cm = None,add_to = self.add_button_tools)
            
            self.button_text = qw.QLineEdit()
            self.parameters.layout().addRow('Text: ',self.button_text)
            
            #Size Grid
            self.size_grid = guts.widget_setup(qw.QWidget(),qw.QGridLayout(),spacing = 5)
            self.parameters.layout().addRow(self.size_grid)
            for i ,setting in enumerate(['width','height']):
                self.widgets[setting + '_text'] = guts.widget_setup(qw.QLabel(setting.title()),None,add_to = [self.size_grid,0,(i*2)])
                self.widgets[setting] = guts.widget_setup(qw.QSpinBox(),None,add_to = [self.size_grid,0,((i*2)+1)])
                self.widgets[setting].setFixedWidth(70)
                self.widgets[setting].setSingleStep(5)
                self.widgets[setting].setMinimum(5)
                self.widgets[setting].setMaximum(400)
                self.widgets[setting].setValue(15)
            
            #Type and Side Settings
            for x in ['side','type']:
                self.widgets[x] = qw.QComboBox()
                self.widgets[x].setFixedWidth(195)
                self.parameters.layout().addRow(x.title() + ': ',self.widgets[x])
                if x == 'side': items = ['center','left','right','none']
                else: items = ['anim','switch','ui','function']
                for item in items: self.widgets[x].addItem(item.replace('_',' ').title().replace('Ui','UI'))
    
            ##Button Function Stack
            self.button_function_stack = qw.QStackedWidget()
            self.parameters.layout().addRow(self.button_function_stack)
            
            for all in ['anim','switch','ui']:
                widget = guts.widget_setup(qw.QWidget(),qw.QHBoxLayout())
                widget.layout().setAlignment(qc.Qt.AlignTop)
                label = guts.widget_setup(qw.QLabel(all.title() + ': '),None,add_to = widget)
                if all in ['anim','ui']: self.button_function_stack.addWidget(widget)
                else: 
                    switch_widget = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout())
                    switch_functions = guts.widget_setup(qw.QWidget(),qw.QGridLayout(),spacing = 2,cm = (5,5,5,5))
                    switch_widget.layout().setAlignment(qc.Qt.AlignTop)
                    switch_widget.layout().addWidget(widget)
                    switch_widget.layout().addWidget(switch_functions)
                    self.button_function_stack.addWidget(switch_widget)
            
                if all in ['anim','switch']:
                    self.widgets[all + '_button_text'] = guts.widget_setup(qw.QLineEdit(),None,add_to = widget)
                    self.widgets['paste_' + all] = guts.widget_setup(qw.QPushButton('<<'),None,add_to = widget)
                    self.widgets[all + '_button_text'].setReadOnly(True)
                    self.widgets['paste_' + all].setFixedSize(20,20)
                    self.widgets['paste_' + all].clicked.connect(partial(self.get_anim,all))
                else:
                    self.widgets[all + '_selection'] = guts.widget_setup(qw.QComboBox(),None,add_to = widget)
                    self.widgets[all + '_selection'].setFixedWidth(210)
                    try:
                        doc = ET.parse(document)
                        root = doc.getroot()
                        frames = root.findall('Frame')
                        self.widgets[all + '_selection'].addItem('none')
                        for frame in frames: self.widgets[all + '_selection'].addItem(frame.get('name'))
                        self.widgets[all + '_selection'].item(0).setSelected(True)
                    except: pass
            
            ####Switch Functions
            for i, s in enumerate(['FK','IK']):
                label = guts.center_label(s + ' Buttons',widget = [switch_functions,0,i])
                self.widgets[s + '_switch_buttons'] = guts.widget_setup(qw.QListWidget(),None,add_to = [switch_functions,1,i])
                self.widgets[s + '_switch_buttons'].setSelectionMode(qw.QAbstractItemView.ExtendedSelection)
            
            ####Function Widget
            func_widget = guts.widget_setup(qw.QWidget(),qw.QVBoxLayout(),spacing = 3)
            func_widget.layout().setAlignment(qc.Qt.AlignTop)
            self.button_function_stack.addWidget(func_widget)
            
            function_label = guts.widget_setup(qw.QLabel('Type a function in Python:'),None,add_to = func_widget)
            self.function_text = guts.widget_setup(qw.QTextEdit(),None,add_to = func_widget)
            self.function_text.setWordWrapMode(qg.QTextOption.WordWrap)
                        
            ##Button Grid
            self.button_function_grid = guts.widget_setup(qw.QWidget(),qw.QGridLayout(),spacing = 5,cm = (5,5,5,5),add_to = self.add_button_tools)
            self.button_function_grid.setFixedHeight(110)
            
            #Buttons
            x = 0
            bottom_buttons = ['add_button','edit_selected','align_x_position','align_y_position','mirror_selected','delete_selected']
            for i, btn in enumerate(bottom_buttons):
                if i > 1: x = 1
                if i > 3: x = 2
                self.widgets[btn] = guts.widget_setup(qw.QPushButton(btn.replace('_',' ').title()),None,add_to = [self.button_function_grid,x,(i - (x * 2))])
                self.widgets[btn].setFixedHeight(30)
            
            #Functions
            self.widgets['type'].currentIndexChanged.connect(self.change_button_functions)
            self.button_text.textChanged.connect(self.update_temp_button)
            for setting in ['width','height']: self.widgets[setting].valueChanged.connect(self.update_temp_button)
            for x in ['side','type']: self.widgets[x].currentIndexChanged.connect(self.update_temp_button)
            for at in ['x','y']: self.widgets['align_' + at + '_position'].clicked.connect(partial(self.align_button_position,at))
            self.widgets['add_button'].clicked.connect(self.add_button)
            self.widgets['mirror_selected'].clicked.connect(self.mirror_selected_buttons)
            self.widgets['delete_selected'].clicked.connect(self.delete_selected_buttons)
            self.update_temp_button()
        
    def change_button_functions(self):
        self.button_function_stack.setCurrentIndex(self.widgets['type'].currentIndex())
    
    def get_anim(self,type):
        #Remove Switch Items
        if type == 'switch':
            for k in ['FK','IK']:
                 amnt = self.widgets[k + '_switch_buttons'].count()
                 for i in range(0,amnt): self.widgets[k + '_switch_buttons'].takeItem(0)
        
        #Add Anim Text and Switch Anims if type is switch
        if len(pm.ls(sl = True)) > 0:
            selected = pm.ls(sl = True)[0]
            obj_name = selected.name().split(':')[-1]
            if type == 'switch' and selected.endswith('_switch'):
                self.widgets['switch_button_text'].setText(obj_name)
                switch = pm.PyNode(self.widgets['switch_button_text'].text())
                
                node = pm.listConnections(switch.connected_to)[0]
                anims = {'FK': pm.listConnections(node.FK_anims),'IK': pm.listConnections(node.IK_anims)}
                for k in anims:
                    for a in anims[k]: self.widgets[k + '_switch_buttons'].addItem(a.name())
                    
            else: self.widgets['anim_button_text'].setText(obj_name)
        else: self.widgets[type + '_button_text'].setText('')
    
    def remove_switch_buttons(self):
        self.widgets[self.ui_switch.currentText().lower() + '_ui'].remove_switch_buttons()
    
    #Aligns the selected Buttons Positions in X and Y on the current Frame
    def align_button_position(self,type):
        frame = self.widgets[self.ui_switch.currentText().lower() + '_ui']
        btns = frame.selected_buttons
        if len(btns) > 1:
            last_btn = frame.buttons[btns[-1]]
            last_btn_pos = last_btn.geometry().center().x()
            if type == 'y': last_btn_pos = last_btn.geometry().center().y()
            if last_btn_pos % 2 == 0: last_btn_pos = last_btn_pos + 1
            for b in btns[:-1]:
                btn = frame.buttons[b]
                if type == 'x': btn.move((last_btn_pos - (btn.width()/2)),btn.y())
                elif type == 'y': btn.move(btn.x(),(last_btn_pos - (btn.height()/2)))
                btn.write_to_xml()
    
    def mirror_selected_buttons(self):
        self.widgets[self.ui_switch.currentText().lower() + '_ui'].mirror_buttons()
      
    def delete_selected_buttons(self):  
        self.widgets[self.ui_switch.currentText().lower() + '_ui'].delete_buttons()
        
    def add_button(self):
        ready = True
        type = self.widgets['type'].currentText().lower()
        
        #Error Message
        if type in ['anim','switch'] and self.widgets[type + '_button_text'].text() == '':
            ready = False
            message = 'No ' + type + ' has been selected for the button.\nPlease select the desired ' + type + ' to proceed.'
        elif type == 'ui' and self.widgets['ui_selection'].currentText() == 'none':
            ready = False
            message = 'No UI has been selected for the button.\nPlease choose a UI for the button to go to.'
        elif type == 'function' and self.function_text.toPlainText() == '':
            ready = False
            message = 'There is no text to generate a python function.\nPlease copy and paste a python code into the text area.'
            
        #Run the funciton.
        if ready == True: self.widgets[self.ui_switch.currentText().lower() + '_ui'].add_button()
        else: error_m = pm.confirmDialog(t = 'ERROR',m = message,b = ['OK'],cb = 'OK')
        
    def update_temp_button(self):
        temp = self.temp_button
        temp.setText(self.button_text.text())
        temp.setFixedSize(self.widgets['width'].value(),self.widgets['height'].value())
        side = self.widgets['side'].currentText().lower()
        type = self.widgets['type'].currentText().lower()
        drag_button_color(temp,side,type)
    
    def default_button_settings(self):
        self.button_text.setText('')
        for all in ['width','height']: self.widgets[all].setValue(15)
        for all in ['side','type']: self.widgets[all].setCurrentIndex(0)
        for all in ['anim','switch']: self.widgets[all + '_button_text']
        self.function_text.setText('')
        
    #=================================================================================================================================#    
    #Changes the color of the buttons based on the anim selection for the rig.
    def selection_change(self):
        #Change Channel Box
        self.channel_box.change_channel_box()
        
        try:
            #Variables
            rig = self.rigs[self.rig_switch.currentIndex()].character_name.get()
            index = self.ui_switch.currentIndex()
            widget = get_frames(self,rig)[index]
            btns = widget.buttons
            root = ET.parse(GUI_LIBRARY + rig + '/.gui.xml').getroot()
            frame = root.findall('Frame')[index]
            self.selected_anims = []
            selected_btns = []
            current_frame = self.widgets[frame.get('name') + '_ui']
            from gui.Meta_Marking_Menu import delete_metacore_marking_menu
            delete_metacore_marking_menu()
            
            #Turns off all the buttons then colors the ones with the selected anims white
            for btn in btns: btns[btn].correct_color()
            for sel in pm.ls(sl = True):
                if ':' in  sel.name(): obj_ref_name = sel.replace(':' + sel.split(':')[-1],'')
                else: obj_ref_name = get_root_rig_from_obj(sel).character_name.get()#.lower()
    
                if obj_ref_name == self.rig_switch.currentText():
                    xml_anim = frame.find("Button/Anim[@name='" + sel.name().split(':')[-1] + "']..")
                    if xml_anim != None:
                        self.selected_anims.append(sel)
                        btn_name = frame.get('name') + '_btn_' + xml_anim.get('number')
                        selected_btns.append(btn_name)
                        drag_button_color(widget.buttons[btn_name],'','anim',selected = True)
        except: pass
    
    #Get Rid of Script Jobs, Timers, and Contexts so they don't run if the tool is gone.
    def closeEvent(self,event):
        try: pm.scriptJob(kill = self.widgets['selection_change'])
        except: pass
        self.channel_box.refresher.stop()
        for win in ['UI_Editor']:
            if pm.window(win,ex=True) == True: pm.deleteUI(win,wnd=True)
        if pm.dragAttrContext( 'channel_box_drag', ex = True) == True: pm.deleteUI('channel_box_drag')
        
#MetaCharacterPicker()