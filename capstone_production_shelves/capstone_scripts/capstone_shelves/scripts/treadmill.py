from pymel.all import *
from metaCore2 import *
import shiboken2, maya, os;

def get_node_from_obj(obj):
    if obj.hasAttr('connected_to'):
        nodes = listConnections(obj.connected_to)
        for node in nodes:
            if node.network_type.get() != 'Multi_Constraint':
                return PyNode(node)

def get_root_rig_from_obj(obj):
    rig = None
    if obj.hasAttr('connected_to'):
        component = PyNode(get_node_from_obj(obj))
        if component.hasAttr('rig'):
            return listConnections(component.rig)[0]
        elif component.hasAttr('character_name'):
            return PyNode(component)
        if rig and rig.hasAttr('connected_to'):
            return PyNode(listConnections(rig.connected_to)[0])

def get_keys(anim):
    keys = []
    for attr in anim.listAttr(w=True,u=True,v=True,k=True):
        key = keyframe(attr,q=True)
        keys += key
        break
    return keys
      
def get_multi_constraint(anim):
    if anim.hasAttr('connected_to'):
        nodes = listConnections(anim.connected_to)
        for node in nodes:
            if node.network_type.get() == 'Multi_Constraint':
                if listConnections(node.anim)[0] == anim:
                    return node

def constraint_switch(anim,node,*arg):
        original_selection = ls(sl = True)
        if True:
            align_loc = group(em = True)
            position_null = None
            anim_null = anim.getParent()
            if anim_null.scaleX.get() == -1: 
                parent(align_loc,anim_null)
                align_loc.translate.set(0,0,0)
                align_loc.rotate.set(0,0,0)
                align_loc.scale.set(1,1,1)
                aligner([align_loc],anim)
                position_null = group(em = True)
                parentConstraint(position_null,align_loc,mo = True)
            else: aligner([align_loc],anim)
        index = 1 #self.widgets[anim + '_cons'].currentIndex()
        anim.parent_to.set(index)
        if True:
            aligner([anim],align_loc)
            delete(align_loc)
            if position_null != None: delete(position_null)
        select(original_selection)

def get_COG(sel):
    root_rig = get_root_rig_from_obj(sel[0])
    components = listConnections(root_rig.connected_networks)
    COG = None
    for component in components:
        if component.network_type.get() == 'COG_Chain':
            COG = listConnections(component.anims)[0]
    return COG
    
def get_IK_anims(sel):
    root_rig = get_root_rig_from_obj(sel[0])
    components = listConnections(root_rig.connected_networks)
    IK_networks = []
    IK_anims = []
    for component in components:
        if component.network_type.get().startswith('FKIK'):
            IK_networks.append(component)
    for net in IK_networks:
        IK_anim = listConnections(net.IK_anims)
        for anim in IK_anim:
            if not 'leg_PV' in anim.name(): IK_anims.append(anim)
    return IK_anims
    
def correct_COG(COG):
    COG_null = COG.getParent()
    grp = group(n = 'corrective_grp',em = True)
    null = group(n = 'corrective_null',em = True,p = grp)
    aligner([grp],COG.getParent())
    aligner([null],COG,position = False)
    for at in ['X','Y','Z']:
        COG_null.attr('translate' + at).unlock()
        COG_null.attr('rotate' + at).unlock()
    parCon = parentConstraint(null,COG_null,mo = True)
    null.rx.set(0)
    delete(parCon)
    for at in ['X','Y','Z']:
        COG_null.attr('translate' + at).lock()
        COG_null.attr('rotate' + at).lock()

class Treadmill():
    def __init__(self):
        sel = ls(sl = True)
        try:
            cog = get_COG(sel)
            root_rig = get_root_rig_from_obj(cog)
            topCon = listConnections(root_rig.topCon)[0]
            comp_grp = listConnections(root_rig.component_grp)[0]
            anims = get_IK_anims(sel)
            topCon.translate.set(0,0,0)
            topCon.rotate.set(0,0,0)
            refresh()
            refresh(suspend = True)
            
            for anim in anims:
                select(anim)
                keys = get_keys(anim)
                
                for key in keys:
                    currentTime(key)
                    setKeyframe()
                
                for key in keys:
                    currentTime(key)
                    node = get_multi_constraint(anim)
                    constraint_switch(anim, node)
                    setKeyframe()
            
            keys = get_keys(cog)
            select(cog)
            
            copyKey(cog, time=(keys[0],keys[-1]), attribute=['translateY', 'translateZ'])
            keyTangent(at = 'translateY',itt = 'linear', ott = 'linear',e = True)
            keyTangent(at = 'translateZ',itt = 'linear', ott = 'linear',e = True)
            layers = ls(type = 'animLayer')
            cog_translation_lyr = animLayer('cog_translation_lyr', addSelectedObjects = True, mute = True)
            pasteKey()
            
            layers = ls(type = 'animLayer')
            refresh(suspend = False)
            
            for key in keys:
                currentTime(key)
                setKeyframe(animLayer = layers[0], v = 0, at='translateY')
                setKeyframe(animLayer = layers[0], v = 0, at='translateZ')
            
            #Compensates the TopCon's rotation to correct the rotation of the COG
            #The COG will always start facing forward.
            currentTime(keys[0])
            comp_grp.ry.set(cog.rx.get() * -1.00)
            self.move_back(cog)
                
            #strike = confirmDialog(t = 'X STRIKE X', m = 'Animation successfully treadmilled!',b = ['SWEET!'], cb = 'SWEET!')
               
        except:
            message = ('Double check to see if any of these issues match.\n\n'
                      "1.) You did not select a topCon or rigged character's anims.\n"
                      '2.) Selected object is not connected to MetaCore component.\n'
                      '3.) Something else.')
            error_message = confirmDialog(t = 'Error: GUTTER BALL!', m = message, b = ['OK'],cb = 'OK')
    
    def move_back(self,COG):
        grp = None
        for comp in listConnections(COG.connected_to):
            if comp.network_type.get() == 'COG_Chain': grp = listConnections(comp.component_grp)[0]
        if grp != None:
            for x in ['X','Y','Z']:
                grp.attr('translate' + x).unlock()
                grp.attr('rotate' + x).unlock()
            null = group(em = True)
            aligner([null],COG)
            null.ty.set(0)
            con = pointConstraint(null,grp,mo = True)
            null.translate.set(0,0,0)
            delete(con,null)
        return grp
        
#Treadmill()