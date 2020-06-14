from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class FK_Chain(Network_Node):
    def __init__(self,side,limb,start,end,translation = False, rotation = True,stretch = True, stretch_mode = 'scale'):
        exists = False

        root = PyNode(start)
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'FK_Chain':
                    if listConnections(node.start)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'FK_Chain',side = side,limb = limb,start = start,end = end)
            network = side.title() + '_' + limb.title() + '_FK_Chain'
            name = side + '_' + limb
            bones = get_chain(start,end);
            anim_null = []
            
            for bone in bones:
                con = check_constraint_connections(bone)
                if con: delete(con)
             
            #IK Setup
            FK = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'FK_anim')
            FK[-1].rename(bones[-1] + '_FK_end')
            
            #Control Joints
            Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_')
            for i in range(0,len(Control)):
                Control[i].rename(name + '_' + str(i + 1) + '_control_joint')
    
            for i in range(0,(len(bones))):
                parentConstraint(FK[i],Control[i])
                parentConstraint(Control[i],bones[i])
            
            for i in range(0,len(bones)-1):
                anim_shape_generator([FK[i]],r=1.00)
            
            for i in range(len(FK)):
                FK[i].drawStyle.set(2)
                if translation == True:
                    if FK[i] != FK[-1]:
                        select(cl=True)
                        null = joint(n=(FK[i].replace('anim','null')),p=(0,0,0))
                        null.drawStyle.set(2)
                        aligner([null],FK[i])
                        joint_orient(null)
                        if FK[i] == FK[0]:
                            anim_null = null
                            parent(FK[0],anim_null)
                            #lock_and_hide_attrs([anim_null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])
                        else:
                            parent(null,FK[i-1])
                            parent(FK[i],null)
                            #lock_and_hide_attrs([null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])
                         
            #Stretch
            if stretch == True and translation == False: FK_stretch(FK)
            if translation == False: lock_and_hide_attrs(FK,['tx','ty','tz'])
            if rotation == False: lock_and_hide_attrs(FK,['rx','ry','rz'])
            lock_and_hide_attrs(FK,['sx','sy','sz','v','radius'])
            select(cl=True)
            if translation == False:
                anim_null = FK[0]
            
            #Scale Stretch Mode
            if stretch == True and stretch_mode == 'scale':
                for bone in bones:
                    for axis in ['X','Y','Z']:
                        connect = listConnections(bone.attr('translate' + axis), p=True)[0]
                        connect // bone.attr('translate' + axis)
                    if bone != bones[-1]:
                        fk_anim = PyNode(bone.replace('_bind_joint', '_FK_anim'))
                        fk_anim.stretch >> bone.scaleX
            
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'))
            hidden_grp = group(Control[0],n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            anim_grp = group(anim_null,n=(name + '_anim_grp'),p=component_grp)
            network_grp_lock(name,bones[0])
            select(cl=True)
    
            #Connections
            PyNode(network).addAttr('translate',at = bool,dv = translation)
            PyNode(network).translate.lock()
            connect_objs_to_node(FK[:-1],network,'anims')
            connect_objs_to_node(FK[:-1],network,'FK_anims')
            connect_objs_to_node(Control,network,'control_joints')
            connect_objs_to_node([component_grp],network,'component_grp')
            connect_objs_to_node([hidden_grp],network,'hidden_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')   