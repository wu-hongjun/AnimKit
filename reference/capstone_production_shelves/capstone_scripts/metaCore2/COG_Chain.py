from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class COG_Chain(Network_Node):
    def __init__(self,side,limb,start,end,stretch = True):
        exists = False

        root = PyNode(start)
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'COG_Chain':
                    if listConnections(node.start)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'COG_Chain',side = side,limb = limb,start = start,end = end)
            network = side.title() + '_' + limb.title() + '_COG_Chain'
            name = side + '_' + limb
            bones = get_chain(start,end);
            
            con = check_constraint_connections(bones[0])
            if con:
                delete(con)
                    
            #COG Setup
            COG = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'COG_anim')
            COG_null = group(n=(name  +  '_COG_null'),em=True)
            aligner([COG_null],bones[0])
            parent(COG[0],COG_null)
            lock_and_hide_attrs(COG,['sx','sy','sz','v','radius'])
            
            #Control Joints
            Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_')
            for i in range(0,len(Control)):
                Control[i].rename(name + '_' + str(i + 1) + '_control_joint')
    
            for i in range(0,(len(bones)-1)):
                parentConstraint(COG[i],Control[i])
                parentConstraint(Control[i],bones[i])
                anim_shape_generator([COG[i]],r=7.00)
            for all in COG:
                PyNode(all).drawStyle.set(2)
            
            select(cl=True)
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'))
            hidden_grp = group(Control[0],n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            anim_grp = group(COG_null,n=(name + '_anim_grp'),p=component_grp)
            network_grp_lock(name,bones[0])
    
            #Connections
            connect_objs_to_node(COG[:-1],network,'anims')
            connect_objs_to_node(Control,network,'control_joints')
            connect_objs_to_node([component_grp],network,'component_grp')
            connect_objs_to_node([hidden_grp],network,'hidden_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')
                
            self.network = network
                
    def auto_translate(self,left_leg,right_leg):
        network = PyNode(self.network)
        COG = listConnections(network.anims)[0]
        COG_null = COG.getParent()
        left_leg = PyNode(left_leg)
        right_leg = PyNode(right_leg)
        right_anim = listConnections(right_leg.IK_anims)[-1]
        left_anim = listConnections(left_leg.IK_anims)[-1]
        
        for all in ['X','Y','Z']: COG.addAttr('auto_translate_' + all,at = 'double',min = 0,max = 1,dv = 0,k = True)
        COG.addAttr('translate_X_divide',at = 'double',min = 2,max = 10,dv = 2,k = True)
        COG.addAttr('translate_Y_divide',at = 'double',min = 2,max = 10,dv = 6,k = True)
        COG.addAttr('translate_Z_divide',at = 'double',min = 2,max = 10,dv = 2,k = True)
        
        auto_translate_null = group(n = COG + '_auto_translate_null', em = True)
        auto_translate = group(n = COG + '_auto_translate', em = True,p=auto_translate_null)
        auto_translate_pos = group(n = COG + '_auto_translate_pos',em = True)
        aligner([auto_translate_null],right_anim,position = False)
        aligner([auto_translate_null],COG,rotation = False)
        aligner([auto_translate_pos],COG)
        
        parent(auto_translate_null,COG_null)
        parent(auto_translate_pos,COG_null)
        parent(COG,auto_translate_pos)
        
        left_md = create_node('multiplyDivide',n = left_anim + '_multiply')
        left_md.input2.set(1,1,-1)
        left_anim.translate >> left_md.input1
        
        pm = shadingNode('plusMinusAverage',au=True)
        left_md.output >> pm.input3D[0]
        right_anim.translate >> pm.input3D[1]
        
        auto_translate_md = create_node('multiplyDivide',n = COG + '_auto_translate_md')
        auto_translate_md.operation.set(2)
        auto_translate_md.input2.set(2,6,2)
        for all in ['X','Y','Z']: COG.attr('translate_' + all + '_divide') >> auto_translate_md.attr('input2' + all)
        pm.output3D >> auto_translate_md.input1
        
        switch = create_node('multiplyDivide',n = COG + '_auto_translate_switch')
        for all in ['X','Y','Z']: COG.attr('auto_translate_' + all) >> switch.attr('input2' + all)
        auto_translate_md.output >> switch.input1
        switch.output >> auto_translate.translate
        
        parentConstraint(auto_translate,auto_translate_pos,mo = True)
        