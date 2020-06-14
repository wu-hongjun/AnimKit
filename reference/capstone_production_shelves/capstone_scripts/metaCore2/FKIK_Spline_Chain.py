from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class FKIK_Spline_Chain(Network_Node):
    def __init__(self,side,limb,start,end,type = 'normal',stretch = True,stretch_mode = 'position'):
        Network_Node.__init__(self,'FKIK_Spline_Chain',side = side,limb = limb,start = start,end = end,stretch = stretch)
        
        network = side.title() + '_' + limb.title() + '_FKIK_Spline_Chain'
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
        IK_curve.inheritsTransform.set(0)
        
        #FK Setup
        FK = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'FK_anim')
        if type == 'normal': anim_shape_generator(FK[:-1])
        else: anim_shape_generator(FK)
        for a in FK:
            a.drawStyle.set(2)
        
        #Control Joints
        Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_')
        for i in range(0,len(Control)):
            Control[i].rename(name + '_' + str(i + 1) + '_control_joint')
            parentConstraint(Control[i],bones[i])
        
        #Switch Setup
        switch = FKIK_switch(name,Control,IK,FK,type)
        
        #Stretch Setup
        if stretch == True:
            switch.addAttr('stretch',min=0,max=1,dv=0,k=True)
            FK_stretch(FK)
            IK_chain_stretch(IK,IK_curve,network,switch)
        
        #Component Grp Organization
        component_grp = group(switch,n=(name + '_component_grp'))
        hidden_grp = group(IK[0],Control[0],IK_handle,IK_curve,n=('DO_NOT_TOUCH'),p=component_grp)
        hidden_grp.visibility.set(0)
        anim_grp = group(n=(name + '_anim_grp'),em=True,p=component_grp)
        FK_anims = group(FK[0],n=(name + '_FK_anim_grp'),p=anim_grp)
        IK_anims = group(IK_anim_info[0],n=(name + '_IK_anim_grp'),p=anim_grp)
        network_grp_lock(name,bones[0])
        
        #IK Twist
        twist_md = create_node('multiplyDivide')
        twist_pma = shadingNode('plusMinusAverage',au=True)
        roll_pma = shadingNode('plusMinusAverage',au=True)
            
        twist_md.input2X.set(-1)
        IK_anim_info[1][0].rotateX >> roll_pma.input1D[0]
        roll_pma.output1D >> IK_handle.roll
        roll_pma.output1D >> twist_md.input1X
            
        IK_anim_info[1][-1].rotateX >> twist_pma.input1D[0]
        twist_md.outputX >> twist_pma.input1D[1]
        twist_pma.output1D >> IK_handle.twist
        
        if type == 'normal':
            #Anim Visibility
            anim_rev = create_node('reverse', n = name + '_anim_vis_reverse')
            anim_md = create_node('multiplyDivide', n = name + '_anim_vis_multiply')
            anim_range = create_node('setRange', n = name + '_anim_vis_range')
            
            anim_md.input2.set(100,100,100)
            anim_range.max.set(1,1,1)
            anim_range.oldMax.set(1,1,1)
            
            switch.FKIK_switch >> anim_rev.inputX
            switch.FKIK_switch >> anim_md.input1X
            anim_rev.outputX >> anim_md.input1Y
            anim_md.output >> anim_range.value
            
            anim_range.outValueX >> IK_anims.visibility
            anim_range.outValueY >> FK_anims.visibility
            
        else:
            #IK Twist
            i=1
            for all in FK:
                PyNode(all).rotateX >> twist_pma.input1D[i + 1];
                i += 1
            FK[0].rotateX >> roll_pma.input1D[1]
            
            #Anim Visibility
            k=0
            for A in ['FK','IK']:
                addAttr(switch,ln=A + '_anim_visibility',at='bool',dv=1,k=True)
                switch.attr(A + '_anim_visibility') >> PyNode(name + '_' + A + '_anim_grp').visibility
            
            for all in IK_anim_info[2]:
                parentConstraint(all.replace('IK_joint','FK_anim'),IK_anim_info[0][k],mo=True)
                k += 1;
                
        select(cl=True)
        
        #Connections
        connect_objs_to_node(FK,network,'anims')
        connect_objs_to_node(IK_anim_info[1],network,'anims')
        connect_objs_to_node(IK_anim_info[1],network,'IK_anims')
        connect_objs_to_node(FK,network,'FK_anims')
        connect_objs_to_node(IK,network,'IK_joints')
        connect_objs_to_node(Control,network,'control_joints')
        connect_objs_to_node([IK_handle],network,'IK_handles')
        connect_objs_to_node([IK_curve],network,'curve')
        connect_objs_to_node([switch],network,'switch')
        connect_objs_to_node([component_grp],network,'component_grp')
        connect_objs_to_node([hidden_grp],network,'hidden_grp')
        
        for anim in listConnections(PyNode(network).anims):
            anim.addAttr('animNode',at='message')