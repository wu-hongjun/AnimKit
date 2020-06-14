from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class Advanced_Hand(Network_Node):
    def __init__(self, side, limb, arm_node, front_loc, back_loc, inner_loc, outer_loc, middle_loc,fingers = []):
        exists = False
        arm = PyNode(arm_node)

        root = listConnections(arm.bones)[-1]
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'Advanced_Hand':
                    if listConnections(node.start)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            arm = PyNode(arm[s])
            wrist = listConnections(arm.bones)[-1]
            PV_Anim, IK_Anim = listConnections(arm.IK_anims)
            switch = listConnections(arm.switch)[-1]
            side = arm.side.get()
            limb = arm.limb.get()
            name = side + '_' + limb
            aligner([PV_Anim],listConnections(arm.bones)[1])
            
            reverse_hand = []
            front = PyNode(front_loc)
            back = PyNode(back_loc)
            inner = PyNode(inner_loc)
            outer = PyNode(outer_loc)
            palm = PyNode(middle_loc)
            wrist = PyNode(wrist)
            finger_tip = PyNode(front_loc)
            hand = [back,inner,outer,front,palm,wrist,palm,front]
            fN = ['rev_palm_base','inner_hand','outer_hand','rev_finger_tip','rev_palm','rev_wrist','rev_rotate_finger','rev_finger_end']
            
            IK_Anim.addAttr('IK_finger_rotation',at = 'double',min = 0,max = 1, dv = 0, k = True)
            IK_Anim.addAttr('wrist_to_finger_tip',at='double',min=-90,max=90,dv=0,k=True)
            IK_Anim.addAttr('palm_lift',at='double',min=-90,max=90,dv=0,k=True)
            IK_Anim.addAttr('side_to_side',at='double',min=-90,max=90,dv=0,k=True)
            IK_Anim.addAttr('wrist_pivot',at='double',min=-90,max=90,dv=0,k=True)
            IK_Anim.addAttr('finger_tip_pivot',at='double',min=-90,max=90,dv=0,k=True)
            
            for i in range(0,8):
                b = joint(n = (name + '_' + fN[i] + '_joint'),p=(0,0,0))
                aligner([b],hand[i])
                b.jointOrient.set(b.rotate.get())
                b.rotate.set(0,0,0)
                reverse_hand.append(b)
                if i > 0:
                    if i == 6: parent(b,reverse_hand[i-3])
                    else: parent(b,reverse_hand[i-1])
                else:
                    rev_grp = group(n=(name + '_rev_hand_grp'),em=True)
                    aligner([rev_grp],IK_Anim)
                    parent(b,rev_grp)
                select(cl=True)
            
            delete(front,back,inner,outer,palm)
            rev_grp.visibility.set(0)
            PyNode(name + '_' + fN[-1] + '_joint').jointOrient.set(0,0,0)
            
            #Side to Side
            in_b = PyNode(reverse_hand[1])
            out_b = PyNode(reverse_hand[2])
                
            side_range = create_node('setRange',n = name + '_rev_hand_side_to_side_sr')
            rev_rot = create_node('multiplyDivide',n = name + '_rev_hand_side_to_side_md')
                
            side_range.min.set(-90,0,0)
            side_range.oldMin.set(-90,0,0)
            side_range.max.set(0,90,0)
            side_range.oldMax.set(0,90,0)
            IK_Anim.side_to_side >> side_range.valueX
            IK_Anim.side_to_side >> side_range.valueY
                
            side_range.outValue >> rev_rot.input1
            rev_rot.input2.set(1,1,1)
    
            rev_rot.outputX >> in_b.rotateZ
            rev_rot.outputY >> out_b.rotateZ
    
            #Palm Lift
            palm_b = PyNode(reverse_hand[4])
            IK_Anim.palm_lift >> palm_b.rx
            
            #Wrist Pivot
            wrist_b = PyNode(reverse_hand[0])
            IK_Anim.wrist_pivot >> wrist_b.ry
            
            #Tip Pivot
            tip_b = PyNode(reverse_hand[3])
            IK_Anim.finger_tip_pivot >> tip_b.ry
            
            #Wrist to tip
            tip_b = PyNode(reverse_hand[3])
            wrist_finger_tip_range = create_node('setRange',n = name + '_rev_hand_wrist_to_finger_tip_sr')
            wrist_finger_tip_rot = create_node('multiplyDivide',n = name + '_rev_hand_wrist_to_finger_tip_md')
            wrist_md = create_node('multiplyDivide',n = name + '_rev_hand_wrist_md')
                
            wrist_finger_tip_range.min.set(-90,0,0)
            wrist_finger_tip_range.oldMin.set(-90,0,0)
            wrist_finger_tip_range.max.set(0,90,0)
            wrist_finger_tip_range.oldMax.set(0,90,0)
            IK_Anim.wrist_to_finger_tip >> wrist_finger_tip_range.valueX
            IK_Anim.wrist_to_finger_tip >> wrist_finger_tip_range.valueY
                
            wrist_finger_tip_range.outValue >> wrist_finger_tip_rot.input1
            wrist_finger_tip_rot.outputX >> wrist_md.input1X
            wrist_md.input2X.set(1)
            
            wrist_finger_tip_rot.input2.set(1,1,1)
            
            wrist_md.outputX >> wrist_b.rotateX
            wrist_finger_tip_rot.outputY >> tip_b.rotateX
            
            reverse_hand.insert(0,rev_grp)
            for finger in fingers:
                select(cl = True)
                hidden_grp = listConnections(finger.hidden_grp)[0]
                start = listConnections(finger.start)[0]
                end = listConnections(finger.end)[0]
                FK = listConnections(finger.FK_anims)[0]
                anim_grp = FK.getParent()
                IK = duplicate_chain(start.name(),end.name(),rep = '_bind',wi = '_IK')
                parent(IK[-1],IK[0])
                delete(IK[1])
                IK_Handle = ikHandle(n=(finger.name() + '_IK'),sol='ikSCsolver',sj=IK[0],ee=IK[-1],ccv=False,pcv=False)[0]
                for a in ['X','Y','Z']: FK.attr('translate' + a).unlock()
                FK_null = joint(n = FK + '_advanced_hand_null')
                FK_null.drawStyle.set(2)
                aligner([FK_null],FK)
                makeIdentity(t = True,r = True,s = True,jo = False,a = True)
                parent(FK,FK_null)
                for a in ['X','Y','Z']: FK.attr('translate' + a).lock()
                parent(IK[0],IK_Handle,hidden_grp)
                parentConstraint(reverse_hand[-1],IK_Handle,mo = True)
                parent(FK_null,anim_grp)
                
                finger_blend = create_node('blendColors',n = finger.name() + '_rotation_blend')
                finger_blend.color2.set(0,0,0)
                switch.FKIK_switch >> finger_blend.blender
                IK[0].rotate >> finger_blend.color1
                
                IK_finger_blend = create_node('blendColors',n = finger.name() + '_IK_rotation_blend')
                IK_finger_blend.color2.set(0,0,0)
                finger_blend.output >> IK_finger_blend.color1
                IK_Anim.IK_finger_rotation >> IK_finger_blend.blender
                
                if PV_Anim.hasAttr('FK_pole_vector'):
                    PV_blend = create_node('blendColors',n = finger.name() + '_PV_rotation_blend')
                    IK_finger_blend.output >> PV_blend.color2
                    PV_blend.color1.set(0,0,0)
                    PV_Anim.FK_pole_vector >> PV_blend.blender
                    PV_blend.output >> FK_null.rotate
                
                else: IK_finger_blend.output >> FK_null.rotate
                
            if IK_Anim.hasAttr('soft_IK'):
                soft_IK = listConnections(arm.IK_handles)[-1]
                delete(soft_IK.getChildren()[0])
                pointConstraint(reverse_hand[-3],soft_IK,mo = True)
    
            con = listConnections(arm.IK_null)[0].getChildren()[0]
            connection_change(con,1,reverse_hand[-3])
            locators = listConnections(arm.locators)
            
            delete(check_constraint_connections(locators[1]))
            parentConstraint(reverse_hand[-3],locators[1],mo=True)
            loc_con = check_constraint_connections(locators[-1])[0]
            connection_change(loc_con,0,reverse_hand[-3])
            
            parent(rev_grp,listConnections(arm.hidden_grp)[0])
            parentConstraint(IK_Anim,rev_grp,mo=True)
            
            wrist_con = listConnections(arm.IK_joints)[-1].getChildren()[0]
            connection_change(wrist_con,0,reverse_hand[-3])
            connect_objs_to_node(reverse_hand,arm,'reverse_hand')
            
            anim_default_pose(PV_Anim)
        
    def connect_components(self,component,connection):
        pass