from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Gestures(Network_Node):
    
    '''Creates component that gives an extra group for setDrivenKeys to exist
    Provides an anim where the user can input the attributes
    Set Driven Keys can be coded using the SDKeycoder in the Rigging Plus Section
    Should only be used with FK_Chains'''
    
    def __init__(self, side, limb, root, controlled_anims, attrs, mins = [], maxs = [], dvs = [], anim = None):
        exists = False

        '''root = PyNode(root)
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Gestures':
                    if listConnections(node.start)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break'''

        if exists == False:
            Network_Node.__init__(self,'Gestures',side = side,limb = limb, root = root)
            
            network = side.title() + '_' + limb.title() + '_Gestures'
            name = side + '_' + limb
            sdk_joints = []
            i = 1
            for c_anim in controlled_anims:
                attributes = listAttr(c_anim, l = True, st = ['translate*','rotate*'])
                for at in attributes: c_anim.attr(at).unlock()
                new_bone = joint(n=(c_anim + '_' + limb +'_SDK_null'),p=(0,0,0),rad = 0.25)
                sdk_joints.append(new_bone)
                aligner([new_bone],c_anim)
                joint_orient(new_bone)
                parent(new_bone,c_anim.getParent())
                parent(c_anim,new_bone)
                for at in attributes:
                    c_anim.attr(at).lock()
                    new_bone.attr(at).lock()
                i += 1
                select(cl = True)
                   
            ##Anim##
            if anim == None:
                anim = joint(n=(name + '_gesture_anim'),p=(0,0,0))
                anim.addAttr('animNode',at='message')
                aligner([anim],root)
                anim_shape_generator([anim],r=0.75)
                anim.drawStyle.set(2)
                joint_orient(anim)
                parentConstraint(root,anim,mo=True)
                lock_and_hide_attrs([anim],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])
                
                #Component Grp Organization
                component_grp = group(n=(name + '_component_grp'),em=True)
                anim_grp = group(anim,n=(name + '_anim_grp'),p=component_grp)
                aligner([anim,component_grp],root)
                network_grp_lock(name,root)
                
                #Newer Connections
                connect_objs_to_node([component_grp],network,'component_grp')
            
            else: anim = PyNode(anim)
            
            for i in range(len(attrs)):
                anim.addAttr(attrs[i], at='double', k=True)
                attribute = anim + '.' + attrs[i]
                if mins: addAttr(attribute,e=True,min = mins[i])
                if maxs: addAttr(attribute,e=True,max = maxs[i])
                if dvs:
                    addAttr(attribute,e=True,dv = dvs[i])
                    anim.attr(attrs[i]).set(dvs[i])
                else:
                    try: v = 0
                    except: v = mins[i]
                    addAttr(attribute,e=True,dv = v)
                    anim.attr(attrs[i]).set(v)
            select(cl=True)
                    
            #Connections
            connect_objs_to_node([anim],network,'anims')
            connect_objs_to_node(sdk_joints,network,'sdk_joints')
            self.network = PyNode(network)
    
    def pre_infinity(self):
        network = PyNode(self.network)
        anim = listConnections(network.anims)[0]
        attrs = listAttr(anim,w=True,u=True,v=True,k=True)
        nodes = []
        for all in attrs:
            items = listConnections(anim.attr(all),c = True,d = True)
            for item in items:
                sdk_node = item[-1]
                try: sdk_node.preInfinity.set(3)
                except: pass
    
    def post_infinity(self):
        network = PyNode(self.network)
        anim = listConnections(network.anims)[0]
        attrs = listAttr(anim,w=True,u=True,v=True,k=True)
        nodes = []
        for all in attrs:
            items = listConnections(anim.attr(all),c = True,d = True)
            for item in items:
                sdk_node = item[-1]
                try: sdk_node.postInfinity.set(3)
                except: pass
        
    def linear(self):
        network = PyNode(self.network)
        anim = listConnections(network.anims)[0]
        attrs = listAttr(anim,w=True,u=True,v=True,k=True)
        nodes = []
        for all in attrs:
            items = listConnections(anim.attr(all),c = True,d = True)
            for item in items:
                sdk_node = item[-1]
                try:
                    selectKey(sdk_node,add = True,k=True)
                    keyTangent(itt = 'linear',ott = 'linear',e = True)
                except: pass
        select(cl = True)
    
    def get_sdk_joints(self):
        network = PyNode(self.network)
        return listConnections(network.sdk_joints)
    
    def hide_joints(self):
        sdk_joints = listConnections(self.network.sdk_joints)
        [x.drawStyle.set(2) for x in sdk_joints]
        
    def show_joints(self):
        sdk_joints = listConnections(self.network.sdk_joints)
        [x.drawStyle.set(0) for x in sdk_joints]
        
    def run_SDK_script(self,file_name):
        if not file_name.endswith('.py'): file_name = file_name + '.py'
        thisDir = os.path.dirname(mc.file(q=1, loc=1)) + '/set_driven_keys'
        items = os.listdir(thisDir)
        if file_name in items:
            script = thisDir + '/' + file_name 
            string = open(script,'r')
            code = {}
            run_code = compile(string.read(),'<string>','exec')
            exec run_code in code
    
    def connect_components(self,component,connection):
        component = PyNode(component)
        network = PyNode(self.network)
        val = len(listConnections(component.connected_networks))
        network.parent_network >> component.connected_networks[val]