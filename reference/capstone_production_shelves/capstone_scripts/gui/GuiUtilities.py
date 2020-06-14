import pymel.all as pm
import maya.cmds as mc
import datetime
import maya.OpenMayaUI as mui
import shiboken2 as shiboken
import xml.etree.ElementTree as ET
from PySide2 import QtCore as qc
from PySide2 import QtWidgets as qw
from PySide2 import QtGui as qg

def get_main_window():
    pointer = mui.MQtUtil.mainWindow();
    return shiboken.wrapInstance(long(pointer), qw.QWidget)
#===============================================================# 
#Indent = Pretty Print Formater found at http://effbot.org/zone/element-lib.htm#prettyprint
def indent(elem, level=0):
    i = "\n" + (level*"\t")
    if len(elem):
        if not elem.text or not elem.text.strip(): elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip(): elem.tail = i
        for elem in elem: indent(elem, level+1)
        if not elem.tail or not elem.tail.strip(): elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()): elem.tail = i

#Corrects the Outliner from showing all the wierd stuff.
def fix_outliner():
    outliners = pm.getPanel(type = 'outlinerPanel')
    [pm.outlinerEditor(x, e = True, sf = 'defaultSetFilter') for x in outliners]
        
#Sets up the PySide Widget with spacing and Contents Margins in one line.
def widget_setup(widget,layout_widget,spacing = 0,cm = (0,0,0,0),w = None, h = None,add_to = None,parent = None):
    widget.setLayout(layout_widget)
    if layout_widget != None:
        if spacing != None: widget.layout().setSpacing(spacing)
        if cm != None: widget.layout().setContentsMargins(cm[0],cm[1],cm[2],cm[3])
    if add_to != None:
        if isinstance(add_to,list): add_to_widget = add_to[0]
        else: add_to_widget = add_to
        type = add_to_widget.layout().__class__.__name__
        if type == 'QFormLayout': add_to_widget.layout().addRow(add_to[1],widget)
        if type == 'QGridLayout': add_to_widget.layout().addWidget(widget,add_to[1],add_to[2])
        else: add_to_widget.layout().addWidget(widget)
    if parent != None: widget.setParent(parent)
    return widget
   
def center_label(txt,widget = None):
    label = qw.QLabel(txt)
    label.setAlignment(qc.Qt.AlignCenter)
    if widget != None:
        try: widget_setup(label,None,add_to = widget)
        except: widget.layout().addWidget(label)
    return label
    
def daytime():
    day = datetime.datetime.now().strftime("%m/%d/%Y")
    time = datetime.datetime.now().strftime("%I:%M %p")
    if day.startswith('0'): day = day[1:]
    if time.startswith('0'): time = time[1:]
    return day, time
    
def publish_xml(root,doc):
    tree = ET.ElementTree(root)
    indent(root)
    tree.write(doc)
    
def string_value_conversion(value):
    if value.isdigit() == True: v = int(value)
    try: v = float(value)
    except:
        if value == 'True': v = 1
        elif value == 'False': v = 0
        else: v = str(value)
    return v
    
def viewport_image(image_size,icon_size):
    globals = pm.PyNode('defaultRenderGlobals')
    globals.imageFormat.set(32)
    p = pm.getPanel( type='modelPanel' )[-1]
    nc = pm.modelEditor(p, q = True, nurbsCurves = True)
    ns = pm.modelEditor(p, q = True, nurbsSurfaces = True)
    pm.modelEditor(p, e = True, nurbsCurves = False, nurbsSurfaces = False)
    
    temp_icon = pm.internalVar(userPrefDir=True) + '/temp_icon.png'
    temp_path = pm.internalVar(userPrefDir=True) + '/temp_image.png'
    asset_image = pm.playblast(frame=[pm.currentTime()], fmt = 'image',v = False, cf = temp_path, wh=image_size, orn = False, p = 100)
    asset_icon = pm.playblast(frame=[pm.currentTime()], fmt = 'image',v = False, cf = temp_icon, wh=icon_size, orn = False, p = 100)

    pm.modelEditor(p, e = True, nurbsCurves = nc, nurbsSurfaces = ns)
    return [temp_icon,temp_path]
    
#This section gets the MARS or MetaCore2 nodes.
def acquire_nodes(obj):
    components = []
    if obj.hasAttr('connected_to'):
        attributes = pm.listConnections(obj.connected_to, p = True)
        for x in attributes:
            if '.anims' in x.name() or '.switch' in x.name() or '.topCon' in x.name():
                components.append(pm.PyNode(x.split('.')[0]))
        return components

def rig_check():
    nodes = []
    rigs = []
    selected = pm.ls(sl = True)
    try:
        for sel in selected: nodes += acquire_nodes(sel)
        for node in nodes:
            if node.hasAttr('topCon'): rigs.append(node)
            elif node.hasAttr('rig'): rigs += pm.listConnections(node.rig)
    except: pass
    return rigs
    
def get_root_rig(rig):
    other_rigs = [rig]
    root = rig
    if rig.hasAttr('connected_to'):
        for r in other_rigs:
            if not r.hasAttr('connected_to'): return r
            else: other_rigs += pm.listConnections(rig.connected_to)
    else: return root
    
def center_combobox(items = None, widget = None):
    cb = qw.QComboBox()
    cb.setEditable(True)
    cb.lineEdit().setReadOnly(True)
    cb.lineEdit().setAlignment(qc.Qt.AlignCenter)
    if items != None: [cb.addItem(x) for x in items]
    if widget != None:
        try: widget_setup(cb,None,add_to = widget)
        except: widget.layout().addWidget(cb)
    return cb
    
def draw_center_scale(rect,sc):
    scaled_rect = qc.QRect(rect)
        
    size = scaled_rect.size()
    pos = scaled_rect.center()
        
    offset = qc.QPoint((pos.x() - (size.width() * 0.5)),(pos.y() - (size.height() * 0.5)))
    scaled_rect.moveCenter(offset)
    scaled_rect.setSize(size * sc)
    scaled_rect.moveCenter(pos)
    return scaled_rect
    
def get_pyside_parent(widget,index = 0,class_type = '*'):
    par = widget.parent()
    if class_type != '*':
        while par.__class__.__name__ != class_type: par = par.parent()
    else:
        for i in range(index): par = par.parent()
    return par 