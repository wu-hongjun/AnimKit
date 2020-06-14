from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class FKIK_Quadruped_Leg(Network_Node):
    def __init__(self, side, limb, start, end, frontLoc, backLoc, innerLoc, outerLoc, stretch = True, soft_IK = True):
        Network_Node.__init__(self,'FKIK_Quadruped_Leg',side = side,limb = limb,start = start,end = end,stretch = stretch)
        
        network = side.title() + '_' + limb.title() + '_FKIK_Quadruped_Leg'
        name = side + '_' + limb
        bones = get_chain(start,end);
        
        con = check_constraint_connections(bones[0])
        if con:
            delete(con)
        
        #IK Setup
        IK = duplicate_chain(start ,end, rep = 'bind_', wi = 'IK_')
        IK_Null = group(n=(name + '_IK_null'),em=True)
        aligner([IK_Null],IK[2])
        IK_Anim = IK_anim_make(name + '_IK',bones[3])
        Leg_IKH = ikHandle(n=(name + '_IK'),sol='ikRPsolver',sj=IK[0],ee=IK[2],ccv=False,pcv=False)[0]
        Foot_IKH = ikHandle(n=IK[2].replace('_joint',''),sol='ikRPsolver',sj=IK[2],ee=IK[3],ccv=False,pcv=False)[0]
        Balltoe_IKH = ikHandle(n=IK[3].replace('_joint',''),sol='ikSCsolver',sj=IK[3],ee=IK[4],ccv=False,pcv=False)[0]
        Toe_IKH = ikHandle(n=IK[4].replace('_joint',''),sol='ikSCsolver',sj=IK[4],ee=IK[5],ccv=False,pcv=False)[0]

        #IK Quad Foot Follow
        quad_start = joint(n=(name + '_quad_IK_joint'),p=(0,0,0))
        quad_end = joint(n=(name + '_quad_IK_end_joint'),p=(0,0,0))
        quad_end.translate.set(1,0,0)
        aligner([quad_start],bones[3],rotation = False)
        quad_IKH = ikHandle(n=(name + '_quad_IK'),sol='ikRPsolver',sj=quad_start,ee=quad_end,ccv=False,pcv=False)[0] 
        IK_Handles = [Leg_IKH,Foot_IKH,Balltoe_IKH,Toe_IKH,quad_IKH]
        quads = [quad_start,quad_IKH]
        select(cl=True)
        
        #IK Foot Setup
        rev = reverse_foot_setup(name,IK_Anim[1],frontLoc,backLoc,innerLoc,outerLoc,bones[-1],bones[-2],bones[-3])
        rev_grp = rev[0]
        reverse_foot = rev[1:]
        delete(frontLoc, backLoc, innerLoc, outerLoc)

        IK_Anim[1].addAttr('stretch',at='double',min=0,max=1,dv=0,k=True)
        IK_Anim[1].addAttr('pole_vector_lock',at='double',min=0,max=1,dv=0,k=True)
        IK_Anim[1].addAttr('soft_IK',at='double',min=0,max=1,dv=0,k=True)
        
        #PV setup
        PV = pole_vector(name,bones[1],distance = abs(bones[0].tx.get() * 1.1))
        PV_chain = duplicate_chain(IK[1],IK[-1],rep = 'IK', wi='PV')
        PV_end = PV_chain[1]
        for all in PV_chain:
            PyNode(all).drawStyle.set(2)
        anim_shape_generator(PV_chain[1:-1])

        PV[1].addAttr('FK_pole_vector',at='double',min=0,max=1,dv=0,k=True)
        PV[1].addAttr('stretch',at='double',min=0,dv=1,k=True)
        lock_and_hide_attrs(PV_chain[2:],['tx','ty','tz','sx','sy','sz','v','radius'])
        
        #FK Setup
        FK = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'FK_anim')
        anim_shape_generator(FK[:-1])
        lock_and_hide_attrs([FK[0]],['tx'])
        lock_and_hide_attrs([FK[1]],['rx','ry'])
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
        limb_dist = distanceDimension(sp=(0,1000,0),ep=(0,1000,1)).getParent().rename(name + '_dist')
        upper_dist = distanceDimension(sp=(1,1000,0),ep=(1,1000,1)).getParent().rename(bones[0].replace('_bind_joint','') + '_dist')
        lower_dist = distanceDimension(sp=(1,1000,1),ep=(1,1000,2)).getParent().rename(bones[1].replace('_bind_joint','') + '_dist')
        
        loc1 = PyNode('locator1').rename(name + '_upper_loc')
        loc2 = PyNode('locator2').rename(name + '_lower_loc')
        loc3 = PyNode('locator3').rename(IK[0].replace('IK_joint','loc'))
        loc4 = PyNode('locator4').rename(IK[1].replace('IK_joint','loc'))
        loc5 = PyNode('locator5').rename(IK[2].replace('IK_joint','loc'))
        
        locs = [loc1,loc2,loc3,loc4,loc5]
        dists = [limb_dist,upper_dist,lower_dist]
        conTo = [IK[0],reverse_foot[-3],IK[0],PV[1],reverse_foot[-3]]
        
        for i in range(0,5):
            aligner([locs[i]],conTo[i],rotation = False)
            
        #Switch and Constraint Setup
        switch = FKIK_switch(name,Control,IK,FK)
        switch.FKIK_switch.set(1)
        
        limb_dist.distance >> soft_end.tx
        parent(quad_start,reverse_foot[-3])
        
        #Make Quad Anim
        #quad_anim, quad_anim_end = joint(n=(name + '_quad_anim'),p =(0,0,0),rad=2.00)
        quad_anim, quad_anim_end = duplicate_chain(bones[2] ,bones[3], rep = 'bind_joint', wi = 'quad_anim',reverse = True)
        quad_anim.drawStyle.set(2)
        quad_anim_end.drawStyle.set(2)
        anim_shape_generator([quad_anim],r=1.00)
        quad_anim_null = group(n = name + '_quad_anim_null',em=True)
        #quad_null = group(n = name + '_quad_null',em=True)
        
        aligner([quad_anim_null],IK_Anim[1])
        #aligner([quad_null],bones[2])
        parent(quad_anim,quad_anim_null)
        quad_anim.rotate.set(0,0,0)
        quad_anim.jointOrient.set(0,0,0)
        parent(quad_anim_null,IK_Anim[1])
        lock_and_hide_attrs([quad_anim],['tx','ty','tz','sx','sy','sz','v','radius'])
        select(cl=True)
        
        #Constraints
        parentConstraint(IK_Anim[1],rev_grp)
        pointConstraint(IK[0],quad_IKH,mo=False)
        pointConstraint(quad_anim_end,soft_IKH,mo=False)
        parentConstraint(quad_anim_end,loc2,mo=False)
        parentConstraint(quad_anim_end,loc5,mo=False)
        parentConstraint(IK_Null,Leg_IKH,mo=True,w=1)
        parentConstraint(reverse_foot[-3],Foot_IKH,mo=False)
        parentConstraint(reverse_foot[-2],Balltoe_IKH,mo=True,w=1)
        parentConstraint(reverse_foot[-1],Toe_IKH,mo=True,w=1)
        parentConstraint(soft_end,IK_Null,mo=True)
        poleVectorConstraint(PV[1],Leg_IKH)
        poleVectorConstraint(PV[1],quad_IKH)
        poleVectorConstraint(PV[1],Foot_IKH)
        parentConstraint(quad_start,quad_anim_null,mo=True)
        parentConstraint(PV[1],loc4,mo=False)
        
        #Component Grp Organization
        component_grp = group(switch,n=(name + '_component_grp'))
        hidden_grp = group(IK[0],Control[0],IK_Handles,IK_Null,dists,rev_grp,locs,softs,n=('DO_NOT_TOUCH'),p=component_grp)
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
            FK_stretch(FK[:-2])
            lock_and_hide_attrs(FK[-2:-1],['tx','ty','tz','sx','sy','sz','v','radius'])
            
            #IK Stretch Nodes
            net = PyNode(network)
            sbc = create_node('blendColors',n = name + '_stretch_bc')
            gsmd = create_node('multiplyDivide',n = name + '_global_scale_md')
            smd = create_node('multiplyDivide',n = name + '_stretch_md')
            cond = create_node('condition',n = name + '_stretch_condition')
            pv_b = create_node('blendColors', n = name + '_PV_md')
            dis = dists[0].getChildren(s=True)[0]
            
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
            
            for ik in IK[:2]:
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

            PV_md = create_node('multiplyDivide',n = name + '_PV_stretch_multiply')
            PV_md.input1X.set(PV_end.translateX.get())
            PV[1].stretch >> PV_md.input2X
            PV_md.outputX >> PV_end.translateX
                       
            if soft_IK == False:
                delete(Leg_IKH + '*parentConstraint1')
                parentConstraint(quad_anim_end,Leg_IKH)
            
            IKH_con = parentConstraint(PV_end,Leg_IKH,mo=True,w=0)
            foot_con = parentConstraint(PV_chain[2],Foot_IKH,mo=True,w=0)
            balltoe_con = parentConstraint(PV_chain[3],Balltoe_IKH,mo=True,w=0)
            toe_con = parentConstraint(PV_chain[4],Toe_IKH,mo=True,w=0)
            loc_con = parentConstraint(PV_end,loc5,mo=False,w=0)
            
            cons = [IKH_con,foot_con,balltoe_con,toe_con,loc_con]
            for con in cons:
                con = PyNode(con)
                attrs = listAttr(con,st=['*W0','*W1'])
                pv_rev = create_node('reverse',n = name + '_' + con + '_reverse')
                    
                PV[1].FK_pole_vector >> pv_rev.inputX
                pv_rev.outputX >> con.attr(attrs[0])
                PV[1].FK_pole_vector >> con.attr(attrs[1])
                
            if soft_IK == True:
                IK_null_con = parentConstraint(quad_anim_end,IK_Null,mo=True)
                attrs = listAttr(IK_null_con,st=['*W0','*W1'])
                ik_rev = create_node('reverse',n = name + '_PV_lock_soft_IK_reverse')
                    
                IK_Anim[1].pole_vector_lock >> ik_rev.inputX
                ik_rev.outputX >> IK_null_con.attr(attrs[0])
                IK_Anim[1].pole_vector_lock >> IK_null_con.attr(attrs[1])
                
            #Align PV_Chain to PV_anim    
            aligner([PV_chain[0]],PV[1])
            parent(PV_end,PV[1])
        
        #Delete First PV_Chain Bone   
        delete(PV_chain[0])
        
        #Soft IK Nodes
        if soft_IK == True:
            node = PyNode(network)
            #di
            di = create_node('multiplyDivide',n = name + 'soft_IK_di_md')
            di.operation.set(2)
            dists[0].distance >> di.input1X
            node.global_scale >> di.input2X
            
            #D
            D = create_node('multiplyDivide',n = name + '_soft_IK_D_md')
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
            neg_di_Ds = create_node('multiplyDivide',n = name + '_negative_md')
            di_minus_Ds.output1D >> neg_di_Ds.input1X
            neg_di_Ds.input2X.set(-1)
            
            #exp(-(di-Ds))
            exp = create_node('multiplyDivide',n = name + '_exp_md')
            exp.operation.set(3)
            exp.input1X.set(2.7182)
            neg_di_Ds.outputX >> exp.input2X
            
            #1 - exp(-(di-Ds))
            one = create_node('multiplyDivide',n = name + '_one_md')
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
            
            #Ds + soft(1 - exp(-(di-Ds)))
            Ds_minus_everything = shadingNode('plusMinusAverage',au=True)
            Ds_minus_everything.operation.set(1)
            Ds.output1D >> Ds_minus_everything.input1D[0]
            soft_times.outputX >> Ds_minus_everything.input1D[1]
            
            #if di > Ds
            cond = create_node('condition', n = name + '_soft_IK_condition')
            cond.operation.set(2)
            Ds_minus_everything.output1D >> cond.colorIfTrueR
            di.outputX >> cond.colorIfFalseR
            di.outputX >> cond.firstTerm
            Ds.output1D >> cond.secondTerm
            
            if stretch == True:
                times_stretch = create_node('multiplyDivide', n = name + 'soft_IK_stretch')
                cond.outColorR >> times_stretch.input1X
                sbc.outputR >> times_stretch.input2X
                times_stretch.outputX >> soft_end.tx
            else:
                cond.outColorR >> soft_end.tx

        #Scale Stretching
        if stretch == 'scale':
            for bone in bones:
                if bone in bones[0:2]:
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
            delete(locs[2:])
            IK_Anim[1].deleteAttr('stretch')
            IK_Anim[1].deleteAttr('pole_vector_lock')
            PV[1].deleteAttr('FK_pole_vector')
            PV[1].deleteAttr('stretch')
            lock_and_hide_attrs(FK,['tx','ty','tz','sx','sy','sz','v','radius'])
            
        if soft_IK == False:
            delete(soft_start)
            IK_Anim[1].deleteAttr('soft_IK')
            if stretch == False:
                parentConstraint(quad_anim_end,Leg_IKH)
               
        #Connections
        anims = FK
        anims.append(PV[1])
        anims.append(IK_Anim[1])
        if stretch == True:
            for pv in PV_chain[1:-1]:
                anims.append(pv)
        connect_objs_to_node(anims,network,'anims')
        connect_objs_to_node([IK_Anim[1],quad_anim],network,'IK_anims')
        connect_objs_to_node(FK,network,'FK_anims')
        connect_objs_to_node(IK,network,'IK_joints')
        connect_objs_to_node(Control,network,'control_joints')
        connect_objs_to_node(IK_Handles,network,'IK_handles')
        connect_objs_to_node([switch],network,'switch')
        connect_objs_to_node([component_grp],network,'component_grp')
        connect_objs_to_node([hidden_grp],network,'hidden_grp')
        
        for anim in listConnections(PyNode(network).anims):
            anim.addAttr('animNode',at='message')
            