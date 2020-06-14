from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class RFKIK_Spline_Chain(Network_Node):
    def __init__(self,side,limb,start,end):
        Network_Node.__init__(self,'RFKIK_Spline_Chain',side = side,limb = limb,start = start,end = end)
        
        network = side.title() + '_' + limb.title() + '_RFKIK_Spline_Chain'
        name = side + '_' + limb
        bones = get_chain(start,end);
        num = len(bones)
        
        con = check_constraint_connections(bones[0])
        if con:
            delete(con)
        
        #IK Setup
        IK = duplicate_chain(start ,end, rep = 'bind_', wi = 'IK_')
        IK_curve = make_spline(name + '_IK',start = start,end = end)
        IK_handle = ikHandle(n=(name + '_IK'),sol='ikSplineSolver',c=IK_curve,sj=IK[0],ee=IK[-1],ccv=False,pcv=False)[0]
        IK_anim_info = IK_chain_anim_make(name,IK,IK_curve)
        IK_chain_stretch(IK,IK_curve,network,switch)
        IK_curve.inheritsTransform.set(0)
        
        #FK Setup
        FK_chain = stacked_chain(start ,end, amnt = 1, rep = 'bind_joint', wi = 'FK_anim')
        FK = FK_chain[1::2]
        anim_shape_generator(FK[:-1])
        for a in FK_chain:
            a.drawStyle.set(2)
        
        rev_FK_chain = stacked_chain(start ,end, amnt = 1, rep = 'bind_joint', wi = 'reverse_FK_anim',reverse = True)
        rev_FK = rev_FK_chain[1::2]
        for a in rev_FK_chain:
            a.drawStyle.set(2)
        parentConstraint(FK_chain[-1],rev_FK_chain[0],mo=True)
        anim_shape_generator(rev_FK[:-1],r=0.50)
        
        #Control Joints
        Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_')
        parent(Control[1:],w=True)
        
        for i in range(0,(len(Control)-1)):
            r = Control[i].replace('control_joint','reverse_FK_anim')
            pointConstraint(r,Control[i],mo=True)
            aimConstraint(Control[i + 1],Control[i],mo=True)
        r = Control[-1].replace('control_joint','reverse_FK_anim')
        parentConstraint(r,Control[-1])
        
        #FK Stretch
        FK_stretch(FK)
        FK_stretch(rev_FK)
        i=-1
        for fk in FK[:-1]:
            r_md = shadingNode('multiplyDivide',au=True)
            r_rot_md = shadingNode('multiplyDivide',au=True)
            fk = PyNode(fk)
            r_fk = PyNode(rev_FK[i]).getParent()
            fk.rotate >> r_rot_md.input1
            r_rot_md.input2.set(-1,-1,-1)
            r_rot_md.output >> r_fk.rotate
            md = Attribute(listConnections(r_fk + '.tx',p=True)[0])
            md >> r_md.input1X
            fk.stretch >> r_md.input2X
            r_md.outputX >> r_fk.translateX
            i=i-1
        lock_and_hide_attrs(FK,['tx'])    
        lock_and_hide_attrs(rev_FK,['tx'])   
        
        #Switch Setup
        switch = FKIK_switch(name,bones,IK,Control,'normal')
        switch.addAttr('FK_to_Reverse_FK',min=0,max=1,dv=0.5,k=True)
        
        #Component Grp Organization
        component_grp = group(switch,n=(name + '_component_grp'))
        hidden_grp = group(IK[0],IK_handle,IK_curve,Control,n=('DO_NOT_TOUCH'),p=component_grp)
        hidden_grp.visibility.set(0)
        anim_grp = group(n=(name + '_anim_grp'),em=True,p=component_grp)
        FK_anims = group(FK_chain[0],rev_FK_chain[0],n=(name + '_FK_anim_grp'),p=anim_grp)
        IK_anims = group(IK_anim_info[0],n=(name + '_IK_anim_grp'),p=anim_grp)
        network_grp_lock(name,bones[0])
        
        #IK Twist
        twist_md = shadingNode('multiplyDivide',au=True)
        twist_pma = shadingNode('plusMinusAverage',au=True)
        roll_pma = shadingNode('plusMinusAverage',au=True)
            
        twist_md.input2X.set(-1)
        IK_anim_info[1][0].rotateX >> roll_pma.input1D[0]
        roll_pma.output1D >> IK_handle.roll
        roll_pma.output1D >> twist_md.input1X
            
        IK_anim_info[1][-1].rotateX >> twist_pma.input1D[0]
        twist_md.outputX >> twist_pma.input1D[1]
        twist_pma.output1D >> IK_handle.twist
        
        #Anim Visibility Toggle
        anim_rev = shadingNode('reverse',au=True)
        anim_md = shadingNode('multiplyDivide',au=True)
        anim_range = shadingNode('setRange',au=True)
            
        anim_md.input2.set(100,100,100)
        anim_range.max.set(1,1,1)
        anim_range.oldMax.set(1,1,1)
            
        switch.FKIK_switch >> anim_rev.inputX
        switch.FKIK_switch >> anim_md.input1X
        anim_rev.outputX >> anim_md.input1Y
        anim_md.output >> anim_range.value
            
        anim_range.outValueX >> IK_anims.visibility
        anim_range.outValueY >> FK_anims.visibility
        
        #FK Anim Visibility Toggle
        fk_anim_rev = shadingNode('reverse',au=True)
        fk_anim_md = shadingNode('multiplyDivide',au=True)
        fk_anim_range = shadingNode('setRange',au=True)
            
        fk_anim_md.input2.set(100,100,100)
        fk_anim_range.max.set(1,1,1)
        fk_anim_range.oldMax.set(1,1,1)
            
        switch.FK_to_Reverse_FK >> fk_anim_rev.inputX
        switch.FK_to_Reverse_FK >> fk_anim_md.input1X
        fk_anim_rev.outputX >> fk_anim_md.input1Y
        fk_anim_md.output >> fk_anim_range.value
            
        fk_anim_range.outValueX >> rev_FK_chain[0].visibility
        fk_anim_range.outValueY >> FK_chain[0].visibility
            
        select(cl=True)
        #Connections
        connect_objs_to_node(FK,network,'anims')
        connect_objs_to_node(rev_FK,network,'anims')
        connect_objs_to_node(IK_anim_info[1],network,'anims')
        connect_objs_to_node(IK,network,'IK_joints')
        connect_objs_to_node(Control,network,'control_joints')
        connect_objs_to_node(IK_handle,network,'IK_handles')
        connect_objs_to_node(IK_curve,network,'curve')
        connect_objs_to_node(switch,network,'switch')
        connect_objs_to_node(component_grp,network,'component_grp')
        connect_objs_to_node(hidden_grp,network,'hidden_grp')
        
        for anim in listConnections(PyNode(network).anims):
            anim.addAttr('animNode',at='message')