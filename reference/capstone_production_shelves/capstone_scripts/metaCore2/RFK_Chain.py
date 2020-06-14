from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class RFK_Chain(Network_Node):
    def __init__(self,side,limb,start,end,translation = False, rotation = True,stretch = True):
        exists = False

        root = PyNode(start)
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'RFK_Chain':
                    if listConnections(node.start)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'RFK_Chain',side = side,limb = limb,start = start,end = end)
            network = side.title() + '_' + limb.title() + '_RFK_Chain'
            name = side + '_' + limb
            bones = get_chain(start,end);
            bones.reverse()
            anim_null = []
            
            for bone in bones:
                con = check_constraint_connections(bone)
                if con: delete(con)
            
            #IK Setup
            RFK = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'RFK_anim',reverse = True)
            #aligner([anim_null],bones[0])
            #parent(FK[0],anim_null)
            
            
            #Control Joints
            Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_',reverse = True)
            for i in range(0,len(Control)):
                Control[i].rename(name + '_' + str(i + 1) + '_control_joint')
            
            for i in range(0,(len(bones)-1)):
                parentConstraint(RFK[i],Control[i])
                parentConstraint(Control[i],bones[i])
                anim_shape_generator([RFK[i]],r=1.00)
            parentConstraint(RFK[-1],Control[-1],mo=True)
            parentConstraint(Control[-1],bones[-1])
            
            for i in range(len(RFK)):
                RFK[i].drawStyle.set(2)
                if translation == True:
                    if RFK[i] != RFK[-1]:
                        select(cl=True)
                        null = joint(n=(RFK[i].replace('anim','null')),p=(0,0,0))
                        null.drawStyle.set(2)
                        aligner([null],RFK[i])
                        joint_orient(null)
                        if RFK[i] == RFK[0]:
                            anim_null = null
                            parent(RFK[0],anim_null)
                            lock_and_hide_attrs([anim_null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])
                        else:
                            parent(null,RFK[i-1])
                            parent(RFK[i],null)
                            lock_and_hide_attrs([null],['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius'])               
            #Stretch
            if stretch == True and translation == False: FK_stretch(RFK)
            if translation == False: lock_and_hide_attrs(RFK,['tx','ty','tz'])
            if rotation == False: lock_and_hide_attrs(RFK,['rx','ry','rz'])
            lock_and_hide_attrs(RFK,['sx','sy','sz','v','radius'])
            select(cl=True)
            if translation == False:
                anim_null = RFK[0]
            
            
            #Component Grp Organization
            component_grp = group(n=(name + '_component_grp'))
            hidden_grp = group(Control[0],n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            anim_grp = group(anim_null,n=(name + '_anim_grp'),p=component_grp)
            network_grp_lock(name,bones[0])
            select(cl=True)
            
            
            #Connections
            connect_objs_to_node(RFK,network,'anims')
            connect_objs_to_node(RFK,network,'FK_anims')
            connect_objs_to_node(Control,network,'control_joints')
            connect_objs_to_node([component_grp],network,'component_grp')
            connect_objs_to_node([hidden_grp],network,'hidden_grp')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')
                
            self.network = network
                
    def auto_hip(self,COG,left_leg,right_leg):
        network = PyNode(self.network)
        axis = ['X','Y','Z']
        COG_anim = listConnections(PyNode(COG).anims)[0]
        left_anim = listConnections(PyNode(left_leg).IK_anims)[-1]
        right_anim = listConnections(PyNode(right_leg).IK_anims)[-1]
        pelvis = listConnections(network.anims)[0]
        pelvis_null = pelvis.getParent()
        pelvis_rot_null = joint(n = pelvis + '_auto_rotate_null',p = (0,0,0))
        select(cl = True)
        pelvis_rot = joint(n = pelvis + '_auto_rotate',p = (0,0,0))
        
        pelvis.addAttr('auto_hip',at = 'double',min = 0,max = 1,dv = 0,k=True)
        for all in axis: pelvis.addAttr('hip_rotate_' + all,at = 'double',min = 0,max = 15,dv = 5,k=True)
        
        aligner([pelvis_rot_null],pelvis)
        aligner([pelvis_rot],pelvis,rotation = False)
        pelvis_rot_null.jointOrient.set(pelvis_rot.rotate.get())
        pelvis_rot_null.drawStyle.set(2)
        pelvis_rot.drawStyle.set(2)
        parent(pelvis_rot_null,pelvis_rot,pelvis_null)
        
        for all in axis: pelvis.attr('translate' + all).unlock()
        parent(pelvis,pelvis_rot_null)
        for all in axis: pelvis.attr('translate' + all).lock()
        
        leg_pm_minus = shadingNode('plusMinusAverage',au = True)
        leg_pm_minus.operation.set(2)
        left_anim.translate >> leg_pm_minus.input3D[0]
        right_anim.translate >> leg_pm_minus.input3D[1]
        
        leg_pm_plus = shadingNode('plusMinusAverage',au = True)
        left_anim.translateX >> leg_pm_plus.input1D[0]
        right_anim.translateX >> leg_pm_plus.input1D[1]
        
        leg_plus_divide = create_node('multiplyDivide',n = network + '_auto_hip_leg_plus_div')
        leg_pm_plus.output1D >> leg_plus_divide.input1X
        leg_plus_divide.input2X.set(-2)
        leg_plus_divide.operation.set(2)
        
        leg_minus_COG = shadingNode('plusMinusAverage',au = True)
        leg_pm_minus.operation.set(2)
        COG_anim.translateY >> leg_minus_COG.input1D[0]
        leg_plus_divide.outputX >> leg_minus_COG.input1D[1]
        if COG_anim.hasAttr('auto_translate_X'):
            COG_anim.getParent().translateY >> leg_minus_COG.input1D[2]
        
        leg_rotation_md = create_node('multiplyDivide',n = network + '_auto_hip_rotation_adjust')
        leg_pm_minus.output3Dx >> leg_rotation_md.input1X
        leg_pm_minus.output3Dy >> leg_rotation_md.input1Y
        leg_minus_COG.output1D >> leg_rotation_md.input1Z
        leg_rotation_md.input2.set(-1,1,1)
        
        hip_md = create_node('multiplyDivide',n = network + '_auto_hip_rotation_md')
        
        leg_rotation_md.outputZ >> hip_md.input1X
        leg_rotation_md.outputX >> hip_md.input1Y
        leg_rotation_md.outputY >> hip_md.input1Z
        for all in axis: pelvis.attr('hip_rotate_' + all) >> hip_md.attr('input2' + all)
        hip_md.output >> pelvis_rot.rotate
        
        bc = create_node('blendColors',n = network + '_auto_hip_blend')
        bc.color2.set(0,0,0)
        hip_md.output >> bc.color1
        pelvis.auto_hip >> bc.blender
        bc.output >> pelvis_rot.rotate
        
        parentConstraint(pelvis_rot,pelvis_rot_null,mo = True)