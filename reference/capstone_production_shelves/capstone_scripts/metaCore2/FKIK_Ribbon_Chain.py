from pymel.all import *
import maya.cmds as mc
import os
from metaCore2.Network_Node import *
from metaCore2.metaUtilities import *
#=======================================================================================================================================================#
class FKIK_Ribbon_Chain(Network_Node):
    def __init__(self,side,limb,start,end,type = 'normal',stretch = True):
        Network_Node.__init__(self,'FKIK_Ribbon_Chain',side = side,limb = limb,start = start,end = end,stretch = stretch)
        
        network = side.title() + '_' + limb.title() + '_FKIK_Ribbon_Chain'
        name = side + '_' + limb
        bones = get_chain(start,end);
        num = len(bones)
        
        con = check_constraint_connections(bones[0])
        if con:
            delete(con)
        
        #IK Setup
        IK = duplicate_chain(start ,end, rep = 'bind_', wi = 'IK_')
        ribbon = make_ribbon(name + '_IK',start = start,end = end)
        IK_anim_info = IK_chain_anim_make(name,IK,ribbon)
        ribbon.inheritsTransform.set(0)
        ribbon_skin(ribbon,IK_anim_info[1])
        parent(IK[1:],w=True)
        
        locator_items = []
        
        for i in range(len(IK)):
            loc = spaceLocator(n= (IK[i].replace('joint','locator')),p=(0,0,0))
            u = i*(1.00/(len(IK)-1))
            n_con = nurbs_constraint(ribbon,loc,u,0.5)
            parentConstraint(loc,IK[i],sr=['x','y','z'],mo = True)
            locator_items.append(loc)
            locator_items.append(n_con)
        
        locs = locator_items[0::2]
        parentConstraint(locs[-1],IK[-1],mo=True)
        
        for i in range(1,len(IK)-1):
            wuo = spaceLocator(n= (IK[i].replace('joint','world_up_locator')),p=(0,0,0))
            grp = group(wuo,n=('temp_grp'))
            wuo.ty.set(1)
            aligner([grp],IK[i])
            parent(wuo,locs[i])
            delete('temp_grp')
            aimConstraint(IK[i + 1],IK[i],wut = 'objectrotation', wu = (0,0,1), wuo = wuo, mo=True)
        
        orientConstraint(locs[0],IK[0],mo=True)    
        select(cl=True)
        #FK Setup
        FK = duplicate_chain(start ,end, rep = 'bind_joint', wi = 'FK_anim')
        anim_shape_generator(FK)
        for a in FK:
            a.drawStyle.set(2)
        
        #Control Joints
        Control = duplicate_chain(start ,end, rep = 'bind_', wi = 'control_')
        for i in range(0,len(Control)):
            Control[i].rename(name + '_' + str(i + 1) + '_control_joint')
            parentConstraint(Control[i],bones[i],mo=False)
        
        #Switch Setup
        switch = FKIK_switch(name,Control,IK,FK,type, v=1.00)
        
        #Stretch Setup
        FK_stretch(FK)
        
        #Component Grp Organization
        component_grp = group(switch,n=(name + '_component_grp'))
        loc_grp = group(locator_items,n=(name + '_locator_grp'))
        hidden_grp = group(loc_grp,IK,Control[0],ribbon,n=('DO_NOT_TOUCH'),p=component_grp)
        hidden_grp.visibility.set(0)
        anim_grp = group(n=(name + '_anim_grp'),em=True,p=component_grp)
        FK_anims = group(FK[0],n=(name + '_FK_anim_grp'),p=anim_grp)
        IK_anims = group(IK_anim_info[0],n=(name + '_IK_anim_grp'),p=anim_grp)
        network_grp_lock(name,bones[0])
        loc_grp.inheritsTransform.set(0)
        
        #IK Twist
        if type == 'normal':
            #Anim Visibility
            anim_rev = create_node('reverse')
            anim_md = create_node('multiplyDivide')
            anim_range = create_node('setRange')
            
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
        #connect_objs_to_node(IK_handle,network,'IK_handles')
        connect_objs_to_node(ribbon,network,'ribbon')
        connect_objs_to_node(switch,network,'switch')
        connect_objs_to_node(component_grp,network,'component_grp')
        connect_objs_to_node(hidden_grp,network,'hidden_grp')
        
        for anim in listConnections(PyNode(network).anims):
            anim.addAttr('animNode',at='message')