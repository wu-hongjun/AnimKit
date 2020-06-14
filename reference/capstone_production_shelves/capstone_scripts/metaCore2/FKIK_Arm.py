from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class FKIK_Arm(Network_Node):
    def __init__(self,side,limb,start,end, stretch = True, soft_IK = True, stretch_mode = 'scale'):
        exists = False

        root = PyNode(start)
        if root.hasAttr('connected_to') and len(listConnections(root.connected_to)) > 0:
            for node in listConnections(root.connected_to):
                if node.hasAttr('network_type') and node.network_type.get() == 'FKIK_Arm':
                    if listConnections(node.start)[0] == root:
                        exists = True
                        self.network = PyNode(node)
                        self.node = str(node)
                        break

        if exists == False:
            Network_Node.__init__(self,'FKIK_Arm',side = side,limb = limb,start = start,end = end,stretch = stretch)
            network = side.title() + '_' + limb.title() + '_FKIK_Arm'
            name = side + '_' + limb
            bones = get_chain(start,end);
            
            for bone in bones:
                con = check_constraint_connections(bone)
                if con: delete(con)
            
            #IK Setup
            IK = duplicate_chain(start ,end, rep = 'bind_', wi = 'IK_')
            IK_Null = group(n=(name + '_IK_null'),em=True)
            IK_Anim = IK_anim_make(name + '_IK',bones[-1],r=1.5)
            IK_Anim[1].addAttr('stretch',at='double',min=0,max=1,dv=0,k=True)
            IK_Anim[1].addAttr('pole_vector_lock',at='double',min=0,max=1,dv=0,k=True)
            IK_Anim[1].addAttr('soft_IK',at='double',min=0,max=1,dv=0,k=True)
            IK_Handle = ikHandle(n=(name + '_IK'),sol='ikRPsolver',sj=IK[0],ee=IK[2],ccv=False,pcv=False)[0]
            
            #PV setup
            PV = pole_vector(name,bones[1],r=1.0,distance = abs(bones[1].tx.get() * 1.1))
            PV[1].addAttr('FK_pole_vector',at='double',min=0,max=1,dv=0,k=True)
            PV[1].addAttr('stretch',at='double',min=0,dv=1,k=True)
            PV_chain = duplicate_chain(IK[1],IK[-1],rep = 'IK_joint', wi='PV_FK_anim')
            PV_end = PV_chain[1]
            PV_end.drawStyle.set(2)
            anim_shape_generator([PV_end],r=1.75)
            aligner([PV_chain[0]],PV[1])
            
            #FK Setup
            FK = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'FK_anim')
            anim_shape_generator(FK,r=1.75)
            for a in FK:
                a.drawStyle.set(2)
            
            #Control Joints
            Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_')
            for i in range(0,len(Control)):
                Control[i].rename(name + '_' + str(i + 1) + '_control_joint')
                parentConstraint(Control[i],bones[i])
            
            #Soft IK Setup
            soft_start = joint(n=(name + '_soft_IK_joint'),p=(0,0,0))
            soft_end = joint(n=(name + '_soft_IK_end_joint'),p=(0,0,0))
            soft_end.translate.set(1,0,0)
            aligner([soft_start],bones[0],rotation = False)
            soft_IKH = ikHandle(n=(name + '_soft_IK'),sol='ikSCsolver',sj=soft_start,ee=soft_end,ccv=False,pcv=False)[0]
            softs = [soft_start,soft_IKH]
    
            #Distance and Locator Setup
            arm_dist = distanceDimension(sp=(0,1000,0),ep=(0,1000,1)).getParent().rename(name + '_dist')
            upper_dist = distanceDimension(sp=(1,1000,0),ep=(1,1000,1)).getParent().rename(bones[0].replace('_bind_joint','') + '_dist')
            lower_dist = distanceDimension(sp=(1,1000,1),ep=(1,1000,2)).getParent().rename(bones[1].replace('_bind_joint','') + '_dist')
            
            loc1 = PyNode('locator1').rename(name + '_upper_loc')
            loc2 = PyNode('locator2').rename(name + '_lower_loc')
            loc3 = PyNode('locator3').rename(IK[0].replace('IK_joint','loc'))
            loc4 = PyNode('locator4').rename(IK[1].replace('IK_joint','loc'))
            loc5 = PyNode('locator5').rename(IK[2].replace('IK_joint','loc'))
            
            locs = [loc1,loc2,loc3,loc4,loc5]
            dists = [arm_dist,upper_dist,lower_dist]
            conTo = [IK[0],IK_Anim[1],IK[0],PV[1],IK_Anim[1]]
            
            for i in range(0,5):
                aligner([locs[i]],conTo[i])
                
            #Switch and Constraint Setup
            switch = FKIK_switch(name,Control,IK,FK)
    
            arm_dist.distance >> soft_end.tx
            
            poleVectorConstraint(PV[1],IK_Handle)
            orientConstraint(IK_Anim[1],IK[2])
            pointConstraint(IK_Anim[1],soft_IKH,mo=False)
            pointConstraint(soft_end,IK_Null,mo=False)
            parentConstraint(IK_Null,IK_Handle,mo=False)
            parentConstraint(IK_Anim[1],loc2,mo=False)
            parentConstraint(PV[1],loc4,mo=False)
            parentConstraint(IK_Anim[1],loc5,mo=False)
    
            #Component Grp Organization
            component_grp = group(switch,n=(name + '_component_grp'))
            hidden_grp = group(IK[0],Control[0],IK_Null,dists,locs,softs,IK_Handle,n=('DO_NOT_TOUCH'),p=component_grp)
            hidden_grp.visibility.set(0)
            anim_grp = group(n=(name + '_anim_grp'),em=True,p=component_grp)
            FK_anims = group(FK[0],n=(name + '_FK_anim_grp'),p=anim_grp)
            IK_anims = group(PV[0],IK_Anim[0],n=(name + '_IK_anim_grp'),p=anim_grp)
            network_grp_lock(name,bones[0])
            
            lock_and_hide_attrs([IK_Anim[1]],['sx','sy','sz','v','radius'])
    
            #Anim Visibility
            FKIK_anim_visibility(switch,IK_anims,FK_anims)
            
            if stretch == True:
                IK_Anim[1].visibility.unlock()
                PV_end = PV_chain[1]
                
                PV_end_md = create_node('multiplyDivide',n = name + '_PV_anim_vis_multiply')
                PV_end_rev = create_node('reverse',n = name + '_PV_anim_vis_reverse')
                PV_end_range = create_node('setRange',n = name + '_PV_anim_vis_range')
                
                PV_end_md.input2.set(100,100,100)
                PV_end_range.max.set(1,1,1)
                PV_end_range.oldMax.set(1,1,1)
                
                PV[1].FK_pole_vector >> PV_end_rev.inputX
                PV[1].FK_pole_vector >> PV_end_md.input1X
                PV_end_rev.outputX >> PV_end_md.input1Y
                PV_end_md.output >> PV_end_range.value
    
                PV_end_range.outValueX >> PV_end.visibility
                PV_end_range.outValueY >> IK_Anim[1].visibility
                PV_end.setAttr('visibility',k=False,cb=False)
                PV_end.setAttr('translateX',k=False,cb=False)
                lock_and_hide_attrs([PV_end],['ty','tz','sx','sy','sz','radius'])
                
                #FK Stretch
                FK_stretch(FK)
                
                #IK Stretch Nodes
                net = PyNode(network)
                sbc = create_node('blendColors',n = name + '_stretch_bc')
                gsmd = create_node('multiplyDivide',n = name + '_global_scale_md')
                smd = create_node('multiplyDivide',n = name + '_stretch_md')
                cond = create_node('condition',n = name + '_stretch_condition')
                pv_b = create_node('blendColors', n = name + '_PV_md')
                dis = dists[0].getShapes()[0]
                
                gsmd.input2X.set(abs(IK[1].translateX.get() + IK[2].translateX.get()))
                
                net.global_scale >> gsmd.input1X
                
                smd.operation.set(2)
                dis.distance >> smd.input1X
                gsmd.outputX >> smd.input2X
    
                smd.outputX >> sbc.color1R
                sbc.color2R.set(1)
                IK_Anim[1].stretch >> sbc.blender
                
                dis.distance >> cond.firstTerm
                gsmd.outputX >> cond.secondTerm
                smd.outputX >> cond.colorIfTrueR
                cond.outColorR >> sbc.color1R
                cond.operation.set(3)
                
                #Pole Vector Stretch
                PV[1].FK_pole_vector >> pv_b.blender
                IK_Anim[1].pole_vector_lock >> pv_b.color2R
                pv_b.color1R.set(1)
                i=1
                
                for ik in IK[:-1]:
                    ik = PyNode(ik)
                    dist = dists[i].getChildren(s=True)[0]
                    
                    bc = create_node('blendColors',n = ik + '_PV_lock_bc')
                    gmd = create_node('multiplyDivide',n = ik + '_PV_lock_global_md')
                    md = create_node('multiplyDivide',n = ik + '_PV_lock_md')
                    
                    dist.distance >> md.input1X
                    md.operation.set(2)
                    
                    net.global_scale >> gmd.input1X
                    gmd.input2X.set(abs(IK[i].translateX.get()))
                    gmd.outputX >> md.input2X
                    
                    md.outputX >> bc.color1R
                    sbc.outputR >> bc.color2R
                    pv_b.outputR >> bc.blender
                    bc.outputR >> ik.scaleX
                    i += 1
    
                PV_md = create_node('multiplyDivide',n = name + '_PV_stretch_md')
                PV_md.input1X.set(PV_end.translateX.get())
                PV[1].stretch >> PV_md.input2X
                PV_md.outputX >> PV_end.translateX
                
                if soft_IK == False:
                    delete(IK_Handle + '*parentConstraint1')
                    parentConstraint(IK_Anim[1],IK_Handle)
                
                IK_end_con = orientConstraint(PV_end,IK[-1])
                IKH_con = parentConstraint(PV_end,IK_Handle,w=0)
                loc_con = parentConstraint(PV_end,loc5,w=0)
                
                cons = [IK_end_con,IKH_con,loc_con]
                for con in cons:
                    con = PyNode(con)
                    attrs = listAttr(con,st=['*W0','*W1'])
                    pv_rev = create_node('reverse',n = name + '_' + con + '_reverse')
                    
                    PV[1].FK_pole_vector >> pv_rev.inputX
                    pv_rev.outputX >> con.attr(attrs[0])
                    PV[1].FK_pole_vector >> con.attr(attrs[1])
                    
                if soft_IK == True:
                    IK_null_con = pointConstraint(IK_Anim[1],IK_Null,mo=False)
                    attrs = listAttr(IK_null_con,st=['*W0','*W1'])
                    ik_rev = create_node('reverse',n = name + '_PV_lock_soft_IK_reverse')
                        
                    IK_Anim[1].pole_vector_lock >> ik_rev.inputX
                    ik_rev.outputX >> IK_null_con.attr(attrs[0])
                    IK_Anim[1].pole_vector_lock >> IK_null_con.attr(attrs[1])
                
            #Soft IK Nodes
            if soft_IK == True:
                node = PyNode(network)
                #di
                di = create_node('multiplyDivide',n = name + '_soft_IK_di')
                di.operation.set(2)
                dists[0].distance >> di.input1X
                node.global_scale >> di.input2X
                
                #D
                D = create_node('multiplyDivide',name + '_soft_IK_D')
                D.input1X.set(abs(IK[1].tx.get() + IK[2].tx.get()))
                D.input2X.set(1)
                
                #Ds = D - soft_IK
                Ds= shadingNode('plusMinusAverage',au=True)
                Ds.operation.set(2)
                D.outputX >> Ds.input1D[0]
                IK_Anim[1].soft_IK >> Ds.input1D[1]
                
                #(di - Ds)
                di_minus_Ds= shadingNode('plusMinusAverage',au=True)
                di_minus_Ds.operation.set(2)
                di.outputX >> di_minus_Ds.input1D[0]
                Ds.output1D >> di_minus_Ds.input1D[1]
                
                #-(di - Ds)
                neg_di_Ds = create_node('multiplyDivide',n = name + 'soft_IK_negative_md')
                di_minus_Ds.output1D >> neg_di_Ds.input1X
                neg_di_Ds.input2X.set(-1)
                
                #exp(-(di-Ds))
                exp = create_node('multiplyDivide',n = name + '_soft_IK_exp_md')
                exp.operation.set(3)
                exp.input1X.set(2.7182)
                neg_di_Ds.outputX >> exp.input2X
                
                #1 - exp(-(di-Ds))
                one = create_node('multiplyDivide',n = name + 'soft_IK_one_md')
                one.input1X.set(1)
                one.input2X.set(1)
                one_minus_exp = shadingNode('plusMinusAverage',au=True)
                one_minus_exp.operation.set(2)
                one.outputX >> one_minus_exp.input1D[0]
                exp.outputX >> one_minus_exp.input1D[1]
                
                #soft(1 - exp(-(di-Ds)))
                soft_times = create_node('multiplyDivide',n = name + '_soft_IK_md')
                one_minus_exp.output1D >> soft_times.input1X
                IK_Anim[1].soft_IK >> soft_times.input2X
                
                
                Ds_minus_everything = shadingNode('plusMinusAverage',au=True)
                Ds_minus_everything.operation.set(1)
                Ds.output1D >> Ds_minus_everything.input1D[0]
                soft_times.outputX >> Ds_minus_everything.input1D[1]
                
                #if di > Ds
                cond = create_node('condition',n = name + '_soft_IK_condition')
                cond.operation.set(2)
                Ds_minus_everything.output1D >> cond.colorIfTrueR
                di.outputX >> cond.colorIfFalseR
                di.outputX >> cond.firstTerm
                Ds.output1D >> cond.secondTerm
                
                if stretch == True:
                    times_stretch = create_node('multiplyDivide',n = name + '_soft_IK_stretch_md')
                    cond.outColorR >> times_stretch.input1X
                    sbc.outputR >> times_stretch.input2X
                    times_stretch.outputX >> soft_end.tx
                    
                else:
                    cond.outColorR >> soft_end.tx
    
            #Scale Stretching
            if stretch_mode == 'scale':
                for bone in bones:
                    if bone != bones[-1]:
                        ik_bone = PyNode(bone.replace('_bind','_IK'))
                        fk_anim = PyNode(bone.replace('_bind_joint', '_FK_anim'))
                        scale_blend = create_node('blendColors',n = bone + '_scale_mode_bc')
                        switch.FKIK_switch >> scale_blend.blender
                        fk_anim.stretch >> scale_blend.color2R
                        ik_scale = listConnections(ik_bone.scaleX,p=True)[0]
                        ik_scale >> scale_blend.color1R
                        scale_blend.outputR >> bone.scaleX
                    for axis in ['X','Y','Z']:
                        connect = listConnections(bone.attr('translate' + axis), p=True)[0]
                        connect // bone.attr('translate' + axis)
    
            #Remove Waste
            if stretch == False:
                delete(locs[2:],PV_chain[1])
                IK_Anim[1].deleteAttr('stretch')
                IK_Anim[1].deleteAttr('pole_vector_lock')
                PV[1].deleteAttr('FK_pole_vector')
                PV[1].deleteAttr('stretch')
                
            if soft_IK == False:
                delete(soft_start)
                IK_Anim[1].deleteAttr('soft_IK')
                if stretch == False:
                    parentConstraint(IK_Anim[1],IK_Handle)
            
            #Add IK Aligners
            i = 1
            IK_aligners = []
            for anim in [PV,IK_Anim]:
                loc = group(n = anim[1] + '_align', em = True)
                parent(loc,anim[0])
                aligner([loc],FK[i])
                parentConstraint(FK[i],loc,mo = True)
                IK_aligners.append(loc)
                i += 1
            
            #Align PV_Chain to PV_anim    
            if stretch == True:
                PV_zero = group(n = PV_end + '_zero_grp',em=True)
                aligner([PV_zero],PV[1].getParent())
                parent(PV_end,PV_zero)
                parent(PV_zero,PV[1].getParent())
                parentConstraint(PV[1],PV_zero,mo=True)
            
            #Delete First PV_Chain Bone
            delete(PV_chain[0])
                    
            select(cl = True)
            
            #Lock FK Attrs
            lock_and_hide_attrs(FK,['tx','ty','tz','sx','sy','sz','v','radius'])
            lock_and_hide_attrs([FK[1]],['rx','ry'])
            
            #Connections
            connect_objs_to_node([PV[1],IK_Anim[1]],network,'IK_anims')
            connect_objs_to_node(FK,network,'FK_anims')
            connect_objs_to_node(IK,network,'IK_joints')
            connect_objs_to_node(Control,network,'control_joints')
            connect_objs_to_node([switch],network,'switch')
            connect_objs_to_node([component_grp],network,'component_grp')
            connect_objs_to_node([hidden_grp],network,'hidden_grp')
            connect_objs_to_node(IK_aligners,network,'IK_aligners')
            connect_objs_to_node([soft_start,soft_end],network,'soft_IK_joints')
            connect_objs_to_node(locs,network,'locators')
            connect_objs_to_node([IK_Null],network,'IK_null')
            if soft_IK == True: connect_objs_to_node([IK_Handle,soft_IKH],network,'IK_handles')
            else: connect_objs_to_node([IK_Handle],network,'IK_handles')
            PyNode(network).addAttr('soft_IK',at = 'bool',dv = soft_IK)
            PyNode(network).soft_IK.lock()

            anims = FK
            anims.append(PV[1])
            anims.append(IK_Anim[1])
            if stretch == True:
                for pv in PV_chain[1:]:
                    anims.append(pv)
            connect_objs_to_node(anims,network,'anims')
            
            for anim in listConnections(PyNode(network).anims):
                anim.addAttr('animNode',at='message')
            
            #self.network = PyNode(network);
            #self.name = name
            
    def advanced_hand(self,front_loc, back_loc, inner_loc, outer_loc, middle_loc, fingers = []):
        arm = PyNode(self.network)
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
        
        connect_objs_to_node([rev_grp],arm,'reverse_hand_grp')
        connect_objs_to_node(reverse_hand,arm,'reverse_hand')
        
        anim_default_pose(PV_Anim)
    
    def anim_deform(self):
        arm = PyNode(self.network)
        wrist = listConnections(arm.bones)[-1]
        IK_Anim = listConnections(arm.IK_anims)[-1]
        hidden_grp = listConnections(arm.reverse_hand_grp)[0]
        reverse_wrist = listConnections(arm.reverse_hand)[-3]
        
        cluster_grp = group(n = IK_Anim + '_cluster_grp', em = True)
        loc = spaceLocator(n = IK_Anim + '_cluster_loc',p = (0,0,0))
        cl = cluster(IK_Anim.name() + '.cv[:]', n = IK_Anim + '_cluster')[1]
        aligner([loc,cluster_grp],cl)
        parent(cl,loc,cluster_grp)
        parent(cluster_grp,hidden_grp)
        
        parentConstraint(reverse_wrist,loc,mo = True)
        loc.translate >> cl.translate
        loc.rotate >> cl.rotate
        cl.inheritsTransform.set(0)
        
        