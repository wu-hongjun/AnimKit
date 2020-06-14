from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Network_Node():
    def __init__(self,network_type,character_name = '',side = '',limb = '',root = '',start = '',end = '',stretch = None):
        
        if network_type not in ['Character_Rig']:
            if network_type not in 'Multi_Constraint': name = side.title() + '_' + limb.title() + '_' + network_type
            else: name = root.title() + '_' + network_type
        else: name = character_name.title() + '_' + network_type
        self.node = name
        
        self.network = createNode('network',n=name)
        self.network.addAttr('network_type',dt='string')
        self.network.addAttr('global_scale',at='double',min=0,dv=1)
        self.network.addAttr('connected_networks',dt='string',m=True)
        
        self.network.setAttr('network_type',network_type,f=True)
        self.network.network_type.lock()
        
        if network_type in ['Character_Rig']:
            root = PyNode(root)
            self.network.addAttr('character_name',dt='string')
            self.network.setAttr('character_name',character_name,f=True)
            self.network.character_name.lock();
            
            connect_objs_to_node([root],self.network,'root')
            self.network.root.lock()
            
            relatives = root.listRelatives(ad=True)
            relatives.insert(0,root)
            relatives =  list(set(relatives))
            
            if network_type == 'Character_Rig':
                for relative in relatives:
                    try:
                        items = str(relative).split('_')[:2]
                        relative.type.set(18)
                        relative.otherType.set(items[1].title())
                        if items[0] == 'center': relative.side.set(0)
                        elif items[0] == 'left': relative.side.set(1)
                        elif items[0] == 'right': relative.side.set(2)
                        else: relative.side.set(3)
                    except: pass
        
        else:
            self.network.addAttr('side',dt='string')
            self.network.addAttr('limb',dt='string')
            
            self.network.setAttr('side',side,f=True)
            self.network.setAttr('limb',limb,f=True)
            
            self.network.side.lock()
            self.network.limb.lock()
            if network_type not in ['Eye_Aim_Anims','Roll_Bone_Chain','Face_Component','Blend_Shape',
                                    'Flexible_Mouth','Flexible_Eyelid','Gestures','Multi_Constraint','Advanced_Hand']:
                bones = get_chain(start,end);
                connect_objs_to_node([bones[0]],self.network,'start')
                connect_objs_to_node([bones[-1]],self.network,'end')
                connect_objs_to_node(bones,self.network,'bones')
            
            self.network.addAttr('rig',at='message')
            self.network.addAttr('parent_network',at='message')
            
            if stretch != None:
                self.network.addAttr('stretch',at='bool',dv=stretch)
                self.network.stretch.lock()

    def __str__(self):
        return self.node
    
    def __repr__(self):
        return self.__str__()

    def get_bones(self):
        type = self.network.network_type.get()
        if self.network.hasAttr('bones'):
            return listConnections(self.network.bones)
    
    def get_control_joints(self):
        if self.network.hasAttr('control_joints'):
            return listConnections(self.network.control_joints)
    
    def get_name(self):
        side = self.network.side.get()
        limb = self.network.limb.get()
        return (side.title() + '_' + limb.title())
    
    def get_network_type(self):
        return self.network.network_type.get()
    
    def get_component_grp(self):
        network = PyNode(self.network)
        if network.hasAttr('component_grp'):
            comp_grp = listConnections(network.component_grp)[0]
            return comp_grp
    
    def get_hidden_grp(self):
        network = PyNode(self.network)
        if network.hasAttr('hidden_grp'):
            hidden_grp = listConnections(network.hidden_grp)[0]
            return hidden_grp
        
    def function_as_written(self):
        try:
            network = PyNode(self.network)
            type = network.network_type.get()
            if type !='Character_Rig':
                try:
                    side = network.side.get()
                    limb = network.limb.get()
                    bones = listConnections(network.bones)
                    start = bones[0]
                    end = bones[-1]
                    if network.hasAttr('stretch') and network.stretch.get() == 0:
                        stretch = network.stretch.get()
                        return "%s('%s','%s','%s','%s',stretch = %s)"%(type,side,limb,start,end,str(stretch))
                    else:
                        return "%s('%s','%s','%s','%s')"%(type,side,limb,start,end)
                    
                except:
                    return 'Error: The Network Node you are looking for no longer exists.'
            else:
                character_name = network.character_name.get()
                root = network.root.get()
                
                return "%s('%s','%s')"%(type,character_name,root)
        except:
            pass;
    
    def IK_to_FK_switch(self):
        if self.network.hasAttr('switch'):
            switch = listConnections(self.network.switch)[0]
            IKs = listConnections(self.network.IK_joints)
            FKs = listConnections(self.network.FK_anims)
            
            for i in range(0,len(FKs)):
                aligner([FKs[i]],IKs[i],position = False)
                if FKs[i].hasAttr('stretch'):
                    FKs[i].stretch.set(IKs[i].sx.get())
    
            switch.FKIK_switch.set(0)
            select(cl=True)
        
    def FK_to_IK_switch(self):
        if self.network.hasAttr('switch'):
            switch = listConnections(self.network.switch)[0]
            IKs = listConnections(self.network.IK_anims)
            IK_aligners = listConnections(self.network.IK_aligners)
            FKs = listConnections(self.network.FK_anims)
                    
            attrs = IKs[0].listAttr(w=True,u=True,v=True,k=True)
            for attr in attrs:
                a = attr.replace((IKs[0] + '.'),'')
                dv = attributeQuery(a,n=IKs[0],ld=True)[0]
                IKs[0].attr(a).set(dv)

            anim_default_pose(IKs[1])
            aligner([IKs[0]],IK_aligners[0])
            aligner([IKs[1]],IK_aligners[1])
            if IKs[1].hasAttr('toe_lift'):
                IKs[1].toe_lift.set(FKs[3].rotateZ.get())
            switch.FKIK_switch.set(1)
            
            for anim in FKs:
                if anim.hasAttr('stretch') and anim.stretch.get() != 1:
                    IKs[1].pole_vector_lock.set(1)
                    IKs[1].stretch.set(1)
                    
            select(cl=True)
    
    def default_pose(self):
        network = PyNode(self.network)
        anims = listConnections(network.anims)
        if network.hasAttr('switch'):
            switch = PyNode(self.get_switch())
            anims.append(switch)
        for anim in anims:
            anim_default_pose(anim)
        select(cl=True)

    def hierarchy_default_pose(self):
        network = PyNode(self.network)
        self.default_pose()
        connections = listConnections(network.connected_networks)
        for connection in connections:
            if connection.hasAttr('connected_networks'):
                connections += listConnections(connection.connected_networks)
            if connection.hasAttr('anims'):
                anims = listConnections(connection.anims)
                for anim in anims:
                    anim_default_pose(anim)
            if connection.hasAttr('switch'):
                anim_default_pose(listConnections(connection.switch)[0])
        select(cl=True)

    def get_switch(self):
        network = PyNode(self.network)
        if network.hasAttr('switch'):
            return listConnections(network.switch)[0]

    def get_all_anims(self):
        network = PyNode(self.network)
        if network.hasAttr('anims'):
            return listConnections(network.anims)
        
    def key_all_anims(self):
        network = PyNode(self.network)
        anims = self.get_all_anims()
        if network.hasAttr('switch'):
            anims.append(PyNode(self.get_switch()))
        for anim in anims:
            for attr in anim.listAttr(w=True,u=True,v=True,k=True):
                attribute = attr.split('.')[-1]
                setKeyframe(anim,at = attribute)

    def select_all_anims(self):
        anims = self.get_all_anims()
        anims.append(self.get_switch())
        select(anims, add = True)
        return anims

    def select_hierarchy_anims(self):
        network = PyNode(self.network)
        anims = self.select_all_anims()
        connections = listConnections(network.connected_networks)
        for connection in connections:
            if connection.hasAttr('connected_networks'):
                connections += listConnections(connection.connected_networks)
            if connection.hasAttr('anims'):
                anims += listConnections(connection.anims)
            if connection.hasAttr('switch'):
                anims += listConnections(connection.switch)
        select(anims, add = True)

    def key_hierarchy(self):
        network = PyNode(self.network)
        anims = self.get_all_anims()
        if network.hasAttr('switch'):
            anims.append(PyNode(self.get_switch()))
        connections = listConnections(network.connected_networks)
        for connection in connections:
            if connection.hasAttr('connected_networks'):
                connections += listConnections(connection.connected_networks)
            if connection.hasAttr('anims'):
                anims += listConnections(connection.anims)
            if connection.hasAttr('switch'):
                anims += listConnections(connection.switch)
        for anim in anims:
            for attr in anim.listAttr(w=True,u=True,v=True,k=True):
                attribute = attr.split('.')[-1]
                setKeyframe(anim,at = attribute)

    def get_FK_anims(self):
        network = PyNode(self.network)
        if network.hasAttr('FK_anims'):
            return listConnections(network.FK_anims)
            
    def get_IK_anims(self):
        network = PyNode(self.network)
        if network.hasAttr('IK_anims'):
            return listConnections(network.IK_anims)
    
    def get_IK_joints(self):
        network = PyNode(self.network)
        if network.hasAttr('IK_joints'):
            return listConnections(network.IK_joints)
    
    def get_net_attr(self,attr_name):
        network = PyNode(self.network)
        if network.hasAttr(attr_name):
            try: return listConnections(network.attr(attr_name))
            except: return network.attr(attr_name).get()
    
    def get_IK_handles(self):
        network = PyNode(self.network)
        if network.hasAttr('IK_handles'): return listConnections(network.IK_handles)
    
    def connect_components(self,component,connection):
        component = PyNode(component)
        network = PyNode(self.network)
        comp_grp = listConnections(network.component_grp)[0]
        attrs = ['tx','ty','tz','rx','ry','rz']
        for all in attrs:
            PyNode(comp_grp).attr(all).unlock()
        if connection == 'start' or connection == 'end':
            if connection == 'start':
                con = listConnections(component.control_joints)[0]
            else:
                con = listConnections(component.control_joints)[-1]
            parentConstraint(con,comp_grp,mo=True)   
        else:
            try:
                con = listConnections(component.bones)
                for c in con:
                    if c == connection:
                        parentConstraint(connection,comp_grp,mo=True)
            except:
                print connection + ' is not part of component ' + component
        val = len(listConnections(component.connected_networks))
        network.parent_network >> component.connected_networks[val]