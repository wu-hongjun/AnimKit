from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Roll_Bone_Chain(Network_Node):
    def __init__(self,side,limb,start,end,roll_bones):
        Network_Node.__init__(self,'Roll_Bone_Chain',side = side,limb = limb,start = start,end = end)
        
        network = side.title() + '_' + limb.title() + '_Roll_Bone_Chain'
        name = side + '_' + limb
        reverse = True

        bones = [PyNode(start), PyNode(end)]
        chain = [PyNode(start), PyNode(end)]
        if bones[1].getParent() != bones[0]: 
            chain.reverse()
            reverse = False
            roll_bones.reverse()
        
        twist = duplicate_chain(chain[0],chain[1],rep = '_bind',wi = '_twist',reverse = reverse)
        twist_null = group(n=(name+'_twist_null'),em=True)
        aligner([twist_null],start)
        parent(twist[0],twist_null)
        
        twist_IK = ikHandle(n=(name + '_twist_IK'),sol='ikSCsolver',sj=twist[0],ee=twist[1],ccv=False,pcv=False)[0]
        
        #Component Grp Organization
        component_grp = group(n=(name + '_component_grp'))
        hidden_grp = group(twist_null,twist_IK,n=('DO_NOT_TOUCH'),p=component_grp)
        hidden_grp.visibility.set(0)
        network_grp_lock(name,bones[0])
        select(cl=True)

        #Roll Bone Setup
        stretch_md = create_node('multiplyDivide')
        chain[1].tx >> stretch_md.input1X
        stretch_md.input2X.set(chain[1].tx.get())
        stretch_md.operation.set(2)
        
        if bones[1].getParent() == bones[0]:
            parentConstraint(bones[0].getParent(), twist_IK, mo=True)
            parentConstraint(bones[0], twist_null, mo=True)
        else:
            parentConstraint(bones[0], twist_IK, mo=True)
            parentConstraint(bones[1], twist_null, mo=True)
        
        for roll_bone in roll_bones:
            md = create_node('multiplyDivide')
            distance_md = create_node('multiplyDivide')
            
            value = float(roll_bone.tx.get()/chain[1].tx.get())
            
            twist[0].rx >> md.input1X
            md.outputX >> roll_bone.rx
            if bones[1].getParent() == bones[0]:
                md.input2X.set(1.00 - value)
            else:
                md.input2X.set(value)
            
            stretch_md.outputX >> distance_md.input2X
            distance_md.input1X.set(roll_bone.tx.get())
            distance_md.outputX >> roll_bone.tx

        select(cl=True)
        
        
        #Connections
        connect_objs_to_node([component_grp],network,'component_grp')
        connect_objs_to_node([hidden_grp],network,'hidden_grp')
        connect_objs_to_node(roll_bones,network,'bones')