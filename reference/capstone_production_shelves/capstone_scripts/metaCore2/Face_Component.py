from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Face_Component(Network_Node):
    def __init__(self,side,limb,bones):
        exists = False

        bone = PyNode(bones[0])
        if bone.hasAttr('connected_to') and len(listConnections(bone.connected_to)) > 0:
            for node in listConnections(bone.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Face_Component':
                    if listConnections(node.bones)[0] == bone:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'Face_Component',side = side,limb = limb)
            
            network = side.title() + '_' + limb.title() + '_Face_Component'
            name = side + '_' + limb
            bones = [PyNode(x) for x in bones]
            nulls = []
            anims = []
            
            for bone in bones:
                con = check_constraint_connections(bone)
                if con: delete(con)
    
            #Anims
            for bone in bones:
                anim = joint(n=(bone.replace('_bind_joint','_anim')),r=0.75,p=(0,0,0))
                null = group(anim,n=(bone.replace('_bind_joint','_null')))
                nulls.append(null)
                anims.append(anim)
                aligner([null],bone)
                rot = anim.rotate.get()
                anim.jointOrient.set(rot)
                anim.rotate.set(0,0,0)
                anim_shape_generator([anim], r=0.25)
                anim.drawStyle.set(2)
                parentConstraint(anim,bone,mo=True)
                lock_and_hide_attrs([anim],['sx','sy','sz','visibility','radius'])
                select(cl=True)
    
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'),em=True)
            anim_grp = group(nulls,n=(name + '_anim_grp'),p=component_grp)
            hidden_grp = group(n=('DO_NOT_TOUCH'),em=True,p=component_grp)
            hidden_grp.visibility.set(0)
            select(cl=True)
            
            #Connections
            connect_objs_to_node(anims,network,'anims')
            connect_objs_to_node(bones,network,'bones')
            connect_objs_to_node([component_grp],network,'component_grp')
            connect_objs_to_node([hidden_grp],network,'hidden_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')
            
            self.network = network
            self.name = name
        
    def connect_components(self,component,connection):
        component = PyNode(component)
        network = PyNode(self.network)
        name = self.name
        comp_grp = listConnections(network.component_grp)[0]
        if connection == 'start' or connection == 'end':
            if connection == 'start':
                con = listConnections(component.control_joints)[0]
            else:
                con = listConnections(component.control_joints)[-1]
            network_grp_lock(name,con)
            attrs = ['tx','ty','tz','rx','ry','rz']
            for all in attrs:
                PyNode(comp_grp).attr(all).unlock()
            parentConstraint(con,comp_grp,mo=True)
        else:
            try:
                con = listConnections(component.bones)
                for c in con:
                    if c == connection:
                        network_grp_lock(name,con)
                        attrs = ['tx','ty','tz','rx','ry','rz']
                        for all in attrs:
                            PyNode(comp_grp).attr(all).unlock()
                        network_grp_lock(name,con)
                        attrs = ['tx','ty','tz','rx','ry','rz']
                        for all in attrs:
                            PyNode(comp_grp).attr(all).unlock()
                        network_grp_lock(name,con)
                        attrs = ['tx','ty','tz','rx','ry','rz']
                        for all in attrs:
                            PyNode(comp_grp).attr(all).unlock()
                        parentConstraint(connection,comp_grp,mo=True)
            except:
                print connection + ' is not part of component ' + component
        val = len(listConnections(component.connected_networks))
        network.parent_network >> component.connected_networks[val]