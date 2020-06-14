from pymel.all import *
import maya.cmds as mc
from functools import partial;
import maya, os;
import xml.dom.minidom as xml
import xml.etree.ElementTree as ET
import maya.OpenMayaUI as mui;
try:
    import shiboken2 as shiboken
    from PySide2 import QtCore as qc;
    from PySide2 import QtWidgets as qg;
except:
    import shiboken
    from PySide import QtCore as qc;
    from PySide import QtGui as qg;
#===============================================================#
def get_main_window():
    pointer = mui.MQtUtil.mainWindow();
    return shiboken.wrapInstance(long(pointer), qg.QWidget)
#===============================================================#
LIBRARY = '//csenetid/cs/unix/projects/instr/capstone3/production/vr/'

def get_scale_settings(rig_title,topCon):
        gs = 1
        pref_file = LIBRARY + '.scale_preferences.xml'
        if os.path.exists(pref_file):
            doc = xml.parse(pref_file)
            for name in doc.getElementsByTagName('rig'):
                if name.getAttribute('id') == rig_title:
                    gs = float(name.getAttribute('scale'))
        topCon.global_scale.set(gs)
        return gs
   
def get_node_from_obj(obj):
    if obj.hasAttr('connected_to'):
        nodes = listConnections(obj.connected_to)
        for node in nodes:
            if node.network_type.get() != 'Multi_Constraint':
                return PyNode(node)

def get_root_rig_from_obj(obj):
    rig = None
    try:
        if obj.hasAttr('connected_to'):
            component = PyNode(get_node_from_obj(obj))
            if component.hasAttr('rig'):
                return listConnections(component.rig)[0]
            elif component.hasAttr('character_name'):
                return PyNode(component)
            if rig and rig.hasAttr('connected_to'):
                return PyNode(listConnections(rig.connected_to)[0])
    except: return None

def get_COG(sel):
    root_rig = get_root_rig_from_obj(sel[0])
    components = listConnections(root_rig.connected_networks)
    COG = None
    for component in components:
        if component.network_type.get() == 'COG_Chain':
            COG = listConnections(component.anims)[0]
    return COG
    
def get_keys(anim):
    keys = []
    for attr in anim.listAttr(w=True,u=True,v=True,k=True):
        key = keyframe(attr,q=True)
        keys += key
    if keys > 1: set(list(set(keys)))
    return keys
    
def get_COG_bone(rig):
    components = listConnections(rig.connected_networks)
    COG = None
    for component in components:
        if component.network_type.get() == 'COG_Chain':
            COG = listConnections(component.start)[0]
    return COG
    
def get_anim_keys(anim):
    keys = []
    for attr in anim.listAttr(w=True,u=True,v=True,k=True):
        key = keyframe(attr,q=True)
        keys += key
        break
    return keys
#===============================================================#
class MotionTracker(qg.QDialog):
    widgets = {}
    def __init__(self):
        original_selection = ls(sl = True)
        file_name = str(sceneName().split('/')[-1])
        scene = file_name.replace('.ma','').replace('.mb','')
        
        if len(original_selection) > 0:
            for all in original_selection:
                try: COG = get_COG(original_selection)
                except: COG = None
                if COG != None:
                    refresh(suspend = True)
                    rig = get_root_rig_from_obj(COG)
                    if referenceQuery(listConnections(rig.topCon), isNodeReferenced=True) == True:
                        ref_name = listConnections(rig.topCon)[0].split(':')[0]
                        cmds.file(referenceQuery(rig, f=True), importReference=True)
                    else: ref_name = rig.character_name.get().lower()
                    COG_b = get_COG_bone(rig)
                    topCon = listConnections(rig.topCon)[0]
                    rig_title = rig.character_name.get()
                    anim_folder = LIBRARY + 'shot/' + scene + '/_animations/' + rig_title + '/locators/'
                    
                    keys = get_anim_keys(COG)
                    if keys and len(keys) > 1:
                        keys = [min(keys), max(keys)]
                        timeRange = str(keys[0]) + ':' + str(keys[1])
                        currentTime(keys[0])
                        gs = get_scale_settings(rig_title,topCon)
                        
                        topCon.translate.set(0,0,0)
                        topCon.rotate.set(0,(COG.rx.get() * -1),0)
                        
                        grp = group(em = True)
                        aligner([grp],COG,rotation = False)
                        grp.ty.set(0)
                        parent(topCon,grp)
                        grp.translate.set(0,0,0)
                        parent(topCon,w = True)
                        select(cl = True)
                        
                        #If for loop does not work, its here #
                        root = joint(n = 'root',p = (0,0,0))
                        rot = joint(n = 'rig_rotation',p = (0,0,0))
                        p_loc = spaceLocator()
                        r_loc = spaceLocator()
                        parent(r_loc,p_loc)
                        parent(root,w=True)
                        
                        aligner([p_loc,r_loc,root],COG_b,rotation = False)
                        pointConstraint(COG_b,p_loc,mo = False)
                        COG_b.rx >> p_loc.ry
                        
                        md = create_node('multiplyDivide')
                        md.input2X.set(-1)
                        p_loc.ry >> md.input1X
                        md.outputX >> r_loc.ry
                        
                        pCon = parentConstraint(p_loc,root,mo = True)
                        oCon = parentConstraint(r_loc,rot,mo = True,st = ['x','z'])
                        size = topCon.global_scale.get()
                        
                        bakeResults(root,rot,time = timeRange)
                        delete(pCon,p_loc,grp)
            
                        #Removes Y translation animation on the locator
                        for at in ['translateY','rotateX','rotateZ']:
                            cutKey(root,at = at,time = timeRange)
                            cutKey(rot,at = at,time = timeRange)
                            root.attr(at).set(0)
                            rot.attr(at).set(0)

                        try: mel.FBXExport(f = anim_folder + ref_name + '@' + scene + '.fbx',s = True)
                        except:
                            path = fileDialog2(fm=2)
                            mel.FBXExport(f = path,s = True)
                        refresh(suspend = False)
                        select(original_selection)
                        topCon.global_scale.set(size)
                        delete(root)
                            
                    else:
                        message = 'No keyframes detected or not enough keyframes found on "' + COG.name() + '."'
                        oops = confirmDialog(t = 'Animation Error',m = message,b = ['OK'],cb = 'OK')
                        if oops == 'OK' and objExists(loc) == True: delete(loc)
                
                else:
                    message = 'Could not find the COG for "' + all.name() + '." What would you like to do?'
                    oops = confirmDialog(t = 'COG Error',m = message, b = ['Continue','Cancel'],cb = 'Cancel')
                    if oops == 'Cancel': break

        else: oops = confirmDialog(t = 'Error',m = 'You must select 1 character.',b = ['OK'],cb = 'OK')
        
#MotionTracker()